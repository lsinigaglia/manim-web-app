"""
Multi-Scene Validation Experiment

Tests whether splitting complex prompts into multiple scenes
produces better results than single-scene generation.
"""
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from app.generator import ManimGenerator
from app.renderer import ManimRenderer
from app.examples import ExampleManager

# Test case: Complex 45-second animation
COMPLEX_PROMPT = """
Create a 45-second animation showing calculus concepts:
1. First, display a coordinate system with the parabola y = x²
2. Then, animate a dot moving along the curve from x=-2 to x=2
3. Finally, show Riemann sum rectangles appearing under the curve to approximate the area
"""

# Approach A: Single scene (current system)
SINGLE_SCENE_PROMPT = COMPLEX_PROMPT

# Approach B: Multi-scene (proposed system)
MULTI_SCENE_PROMPTS = [
    "Create a 15-second animation: show coordinate axes and plot the parabola y = x² in yellow",
    "Create a 15-second animation: show a red dot moving along the parabola y = x² from x=-2 to x=2",
    "Create a 15-second animation: show Riemann sum rectangles appearing under the parabola y = x² from x=0 to x=2"
]


async def test_single_scene():
    """Approach A: Generate as one complex scene."""
    print("\n" + "="*60)
    print("APPROACH A: Single Scene Generation")
    print("="*60)

    generator = ManimGenerator()
    renderer = ManimRenderer()
    examples_manager = ExampleManager()

    # Get relevant examples
    examples = examples_manager.search_examples(SINGLE_SCENE_PROMPT, max_results=2)
    print(f"\nExamples retrieved: {[ex['name'] for ex in examples]}")

    # Generate
    print("\nGenerating code...")
    result = await generator.generate(SINGLE_SCENE_PROMPT, examples)

    if result["status"] == "error":
        print(f"[FAIL] Generation failed: {result['error']}")
        return {
            "success": False,
            "error": result["error"],
            "code_length": 0
        }

    print(f"[OK] Code generated ({len(result['scene_code'])} chars)")
    print(f"\nPlan:\n{result['plan']}")

    # Save code
    scene_path = Path("generated/scene_single.py")
    scene_path.write_text(result["scene_code"])
    print(f"\nCode saved to: {scene_path}")

    # Render
    print("\nRendering...")
    render_result = await renderer.render(scene_path)

    if render_result["status"] == "error":
        print(f"[FAIL] Rendering failed: {render_result['error'][:200]}...")
        return {
            "success": False,
            "error": render_result["error"],
            "code_length": len(result['scene_code']),
            "code": result['scene_code']
        }

    print(f"[OK] Rendering succeeded")

    return {
        "success": True,
        "code_length": len(result['scene_code']),
        "code": result['scene_code'],
        "video_path": render_result["video_path"],
        "plan": result["plan"]
    }


async def test_multi_scene():
    """Approach B: Generate as multiple simple scenes."""
    print("\n" + "="*60)
    print("APPROACH B: Multi-Scene Generation")
    print("="*60)

    generator = ManimGenerator()
    renderer = ManimRenderer()
    examples_manager = ExampleManager()

    results = []

    for i, prompt in enumerate(MULTI_SCENE_PROMPTS, 1):
        print(f"\n--- Scene {i}/3 ---")
        print(f"Prompt: {prompt[:60]}...")

        # Get relevant examples
        examples = examples_manager.search_examples(prompt, max_results=2)
        print(f"Examples: {[ex['name'] for ex in examples]}")

        # Generate
        print("Generating code...")
        result = await generator.generate(prompt, examples)

        if result["status"] == "error":
            print(f"[FAIL] Scene {i} generation failed: {result['error']}")
            results.append({
                "scene": i,
                "success": False,
                "error": result["error"]
            })
            continue

        print(f"[OK] Code generated ({len(result['scene_code'])} chars)")

        # Save code
        scene_path = Path(f"generated/scene_multi_{i}.py")
        scene_path.write_text(result["scene_code"])

        # Render
        print("Rendering...")
        render_result = await renderer.render(scene_path)

        if render_result["status"] == "error":
            print(f"[FAIL] Scene {i} rendering failed: {render_result['error'][:200]}...")
            results.append({
                "scene": i,
                "success": False,
                "error": render_result["error"],
                "code_length": len(result['scene_code']),
                "code": result['scene_code']
            })
            continue

        print(f"[OK] Scene {i} rendered successfully")

        results.append({
            "scene": i,
            "success": True,
            "code_length": len(result['scene_code']),
            "code": result['scene_code'],
            "video_path": render_result["video_path"],
            "plan": result["plan"]
        })

    # Summary
    successful = sum(1 for r in results if r["success"])
    print(f"\n{'='*60}")
    print(f"Multi-scene summary: {successful}/3 scenes succeeded")
    print(f"{'='*60}")

    return results


async def compare_results():
    """Run both approaches and compare."""
    print("\n" + "#"*60)
    print("# MULTI-SCENE VALIDATION EXPERIMENT")
    print("#"*60)

    # Test single scene
    single_result = await test_single_scene()

    # Test multi-scene
    multi_results = await test_multi_scene()

    # Analysis
    print("\n" + "="*60)
    print("COMPARISON ANALYSIS")
    print("="*60)

    print("\n📊 Success Rate:")
    print(f"  Single-scene: {'[OK] Success' if single_result['success'] else '[FAIL] Failed'}")
    multi_success = sum(1 for r in multi_results if r['success'])
    print(f"  Multi-scene:  {multi_success}/3 scenes succeeded ({multi_success/3*100:.0f}%)")

    if single_result['success']:
        print(f"\n📝 Code Complexity:")
        print(f"  Single-scene: {single_result['code_length']} chars")
        total_multi = sum(r.get('code_length', 0) for r in multi_results)
        print(f"  Multi-scene:  {total_multi} chars total ({total_multi/3:.0f} chars/scene avg)")

    print("\n🎯 Verdict:")

    if single_result['success'] and multi_success == 3:
        print("  [WARN]  Both approaches succeeded!")
        print("  → Single-scene might be simpler for this case")
        print("  → But multi-scene allows fixing individual parts")
    elif single_result['success'] and multi_success < 3:
        print("  [OK] Single-scene wins")
        print("  → Multi-scene decomposition didn't help")
    elif not single_result['success'] and multi_success > 0:
        print("  [OK] Multi-scene wins!")
        print(f"  → Single-scene failed completely")
        print(f"  → Multi-scene: {multi_success} partial successes")
        print("  → Easier to fix failures in isolated scenes")
    else:
        print("  [FAIL] Both approaches failed")
        print("  → Need better examples or prompt engineering")

    # Save detailed report
    report_path = Path("generated/experiment_report.txt")
    with open(report_path, "w") as f:
        f.write("MULTI-SCENE VALIDATION EXPERIMENT\n")
        f.write("="*60 + "\n\n")

        f.write("APPROACH A: Single Scene\n")
        f.write("-"*60 + "\n")
        f.write(f"Success: {single_result['success']}\n")
        if single_result['success']:
            f.write(f"Code length: {single_result['code_length']}\n")
            f.write(f"\nGenerated code:\n{single_result.get('code', 'N/A')}\n")
        else:
            f.write(f"Error: {single_result.get('error', 'Unknown')}\n")

        f.write("\n\nAPPROACH B: Multi-Scene\n")
        f.write("-"*60 + "\n")
        for i, result in enumerate(multi_results, 1):
            f.write(f"\nScene {i}:\n")
            f.write(f"  Success: {result['success']}\n")
            if result['success']:
                f.write(f"  Code length: {result['code_length']}\n")
            else:
                f.write(f"  Error: {result.get('error', 'Unknown')[:200]}\n")

    print(f"\n📄 Detailed report saved to: {report_path}")

    return {
        "single": single_result,
        "multi": multi_results
    }


if __name__ == "__main__":
    asyncio.run(compare_results())
