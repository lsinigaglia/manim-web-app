"""
Manim source code chunker using Python AST.

Parses the installed Manim package to extract class-level documentation
chunks suitable for embedding and retrieval.
"""
import ast
import inspect
import textwrap
from pathlib import Path
from typing import List, Dict, Any


class ManimChunker:
    """Extracts structured chunks from the Manim library source."""

    def __init__(self):
        self._manim_path = self._find_manim_source()

    def _find_manim_source(self) -> Path:
        """Locate the installed Manim package source directory."""
        try:
            import manim
            return Path(inspect.getfile(manim)).parent
        except ImportError:
            raise RuntimeError("Manim is not installed. Run: pip install manim")

    def extract_chunks(self) -> List[Dict[str, Any]]:
        """
        Extract all API chunks from the Manim source.

        Returns list of dicts with keys:
            - id: unique identifier (module.ClassName or module)
            - type: "class" or "module"
            - name: class/module name
            - module: full module path
            - content: formatted text for embedding
            - bases: list of base class names (for classes)
            - methods: list of method signatures (for classes)
        """
        chunks = []
        py_files = list(self._manim_path.rglob("*.py"))

        for py_file in py_files:
            rel_path = py_file.relative_to(self._manim_path)
            module_name = "manim." + str(rel_path.with_suffix("")).replace("\\", ".").replace("/", ".")

            # Skip test files, __pycache__, etc.
            if "__pycache__" in str(py_file) or "_test" in py_file.name:
                continue

            try:
                source = py_file.read_text(encoding="utf-8", errors="ignore")
                tree = ast.parse(source)
            except (SyntaxError, UnicodeDecodeError):
                continue

            # Extract module-level docstring
            module_doc = ast.get_docstring(tree)
            if module_doc and len(module_doc.strip()) > 20:
                chunks.append({
                    "id": module_name,
                    "type": "module",
                    "name": rel_path.stem,
                    "module": module_name,
                    "content": f"Module: {module_name}\n\n{module_doc.strip()}",
                    "bases": [],
                    "methods": [],
                })

            # Extract class-level chunks
            for node in ast.walk(tree):
                if not isinstance(node, ast.ClassDef):
                    continue

                class_name = node.name
                bases = [self._get_name(b) for b in node.bases]
                docstring = ast.get_docstring(node) or ""
                methods = self._extract_method_signatures(node)

                # Build content string for embedding
                content_parts = [
                    f"Class: {class_name}",
                    f"Module: {module_name}",
                    f"Bases: {', '.join(bases)}" if bases else "",
                ]

                if docstring:
                    # Truncate very long docstrings
                    doc_lines = docstring.strip().split("\n")
                    if len(doc_lines) > 30:
                        doc_lines = doc_lines[:30] + ["..."]
                    content_parts.append(f"\nDocstring:\n{chr(10).join(doc_lines)}")

                if methods:
                    content_parts.append(f"\nMethods:\n" + "\n".join(f"  - {m}" for m in methods))

                content = "\n".join(p for p in content_parts if p)

                chunks.append({
                    "id": f"{module_name}.{class_name}",
                    "type": "class",
                    "name": class_name,
                    "module": module_name,
                    "content": content,
                    "bases": bases,
                    "methods": methods,
                })

        return chunks

    def _extract_method_signatures(self, class_node: ast.ClassDef) -> List[str]:
        """Extract method signatures from a class definition."""
        methods = []
        for item in class_node.body:
            if not isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue

            # Skip private methods (but keep __init__ and dunder methods)
            if item.name.startswith("_") and not item.name.startswith("__"):
                continue

            sig = self._format_signature(item)
            methods.append(sig)

        return methods

    def _format_signature(self, func_node: ast.FunctionDef) -> str:
        """Format a function/method signature."""
        args = []
        all_args = func_node.args

        # Regular args
        for i, arg in enumerate(all_args.args):
            name = arg.arg
            if name == "self":
                continue
            annotation = ""
            if arg.annotation:
                annotation = f": {ast.unparse(arg.annotation)}"
            args.append(f"{name}{annotation}")

        # *args
        if all_args.vararg:
            args.append(f"*{all_args.vararg.arg}")

        # **kwargs
        if all_args.kwarg:
            args.append(f"**{all_args.kwarg.arg}")

        ret = ""
        if func_node.returns:
            ret = f" -> {ast.unparse(func_node.returns)}"

        return f"{func_node.name}({', '.join(args)}){ret}"

    def _get_name(self, node: ast.expr) -> str:
        """Get name string from an AST node."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_name(node.value)}.{node.attr}"
        elif isinstance(node, ast.Subscript):
            return ast.unparse(node)
        return ast.unparse(node)
