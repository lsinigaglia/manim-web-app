"""
LLM-based Manim code generation.
"""
import os
import json
import re
from typing import List, Dict, Any
from anthropic import AsyncAnthropic


class ManimGenerator:
    """Generates Manim code using Claude."""

    def __init__(self):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")

        self.client = AsyncAnthropic(api_key=api_key)
        self.model = "claude-sonnet-4-5-20250929"

    async def generate(self, prompt: str, examples: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate Manim scene code from prompt and examples.

        Returns:
            {
                "status": "success" | "error",
                "plan": str,
                "scene_code": str,
                "notes": str,
                "error": str (if error)
            }
        """
        try:
            # Build system prompt with examples
            system_prompt = self._build_system_prompt(examples)

            # Build user prompt
            user_prompt = f"""Generate a Manim Community animation for this request:

{prompt}

Remember:
- Keep the animation 8-15 seconds
- Use only Manim Community v0.18.0 compatible APIs
- Return strict JSON format as specified
- Create exactly one Scene class
"""

            # Call Claude
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )

            # Extract JSON from response
            content = response.content[0].text
            result = self._extract_json(content)

            if not result:
                return {
                    "status": "error",
                    "error": f"Failed to parse LLM response as JSON. Response: {content[:500]}"
                }

            # Build complete scene file
            scene_code = self._build_scene_file(
                imports=result.get("imports", ""),
                scene_code=result.get("scene_code", ""),
                notes=result.get("notes", "")
            )

            # Convert plan list to string if needed
            plan = result.get("plan", "")
            if isinstance(plan, list):
                plan = "\n".join(f"{i+1}. {step}" for i, step in enumerate(plan))

            return {
                "status": "success",
                "plan": plan,
                "scene_code": scene_code,
                "notes": result.get("notes", "")
            }

        except Exception as e:
            return {
                "status": "error",
                "error": f"Generation failed: {str(e)}"
            }

    async def fix_error(self, original_code: str, prompt: str, traceback: str) -> Dict[str, Any]:
        """
        Fix a compilation error with minimal patch.

        Returns:
            {
                "status": "success" | "error",
                "fixed_code": str,
                "error": str (if error)
            }
        """
        try:
            system_prompt = """You are a Manim Community expert fixing compilation errors.

Rules:
1. Make the SMALLEST possible change to fix the error
2. Do NOT rewrite or refactor the code
3. Only fix the specific issue shown in the traceback
4. If the error is an API version mismatch, update only that specific call
5. Return the COMPLETE fixed code (not a diff)
6. Use only Manim Community v0.18.0 compatible APIs

Return your response as JSON with this exact format:
{
    "analysis": "brief explanation of the error",
    "fix": "what you changed",
    "fixed_code": "complete fixed scene.py file"
}
"""

            user_prompt = f"""Original prompt: {prompt}

Current code:
```python
{original_code}
```

Error traceback:
```
{traceback}
```

Fix this error with the minimal possible change. Return the complete fixed code.
"""

            response = await self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )

            content = response.content[0].text
            result = self._extract_json(content)

            if not result or "fixed_code" not in result:
                return {
                    "status": "error",
                    "error": f"Failed to parse fix response. Response: {content[:500]}"
                }

            # Unescape literal \n characters if present
            fixed_code = result["fixed_code"].replace('\\n', '\n').replace('\\t', '\t')

            return {
                "status": "success",
                "fixed_code": fixed_code
            }

        except Exception as e:
            return {
                "status": "error",
                "error": f"Fix generation failed: {str(e)}"
            }

    def _build_system_prompt(self, examples: List[Dict[str, Any]]) -> str:
        """Build system prompt including example code."""
        prompt = """You are a Manim Community animation expert. You generate clean, working Manim scenes.

CRITICAL RULES:
1. Use ONLY Manim Community v0.18.0 APIs (not 3b1b/manim legacy)
2. Keep animations SHORT: 8-15 seconds by default
3. Return ONLY valid JSON with this exact structure:
{
    "plan": ["step 1", "step 2", ...],
    "imports": "from manim import *\\n...",
    "scene_code": "class MyScene(Scene):\\n    ...",
    "notes": "assumptions and tweaks"
}

4. Create exactly ONE Scene class
5. Prefer these building blocks:
   - Axes, NumberPlane
   - ValueTracker, always_redraw
   - Create, Write, Transform, FadeIn, FadeOut
6. NO external assets (images, SVG, etc.)
7. Keep object counts low for performance
8. CRITICAL: DO NOT use Text, MathTex, Tex, or axis labels (LaTeX not configured)
   - Use shapes and animations only (Circle, Square, Line, Dot, etc.)
   - If axes are needed, create them WITHOUT labels
   - Focus on visual animations, not text

"""

        # Add examples if provided
        if examples:
            prompt += "\n\nREFERENCE EXAMPLES (adapt to v0.18.0):\n\n"
            for i, ex in enumerate(examples[:2], 1):  # Max 2 examples
                prompt += f"Example {i}: {ex.get('name', 'Unnamed')}\n"
                prompt += f"Tags: {', '.join(ex.get('tags', []))}\n"
                prompt += "```python\n"
                prompt += ex.get('code', '')
                prompt += "\n```\n"
                if ex.get('notes'):
                    prompt += f"Notes: {ex['notes']}\n"
                prompt += "\n"

        return prompt

    def _extract_json(self, text: str) -> Dict[str, Any]:
        """Extract JSON from LLM response (handling markdown code blocks)."""
        # Try to find JSON in code blocks
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass

        # Try to find raw JSON
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass

        return None

    def _build_scene_file(self, imports: str, scene_code: str, notes: str) -> str:
        """Assemble the complete scene.py file."""
        # Unescape literal \n characters if present
        imports = imports.replace('\\n', '\n').replace('\\t', '\t')
        scene_code = scene_code.replace('\\n', '\n').replace('\\t', '\t')
        notes = notes.replace('\\n', '\n')

        header = f'''"""
Generated Manim scene.

Notes:
{notes}
"""

'''
        return header + imports.strip() + "\n\n" + scene_code.strip() + "\n"
