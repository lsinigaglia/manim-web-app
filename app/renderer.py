"""
Direct Manim rendering (programmatic, no subprocess).
"""
import sys
import time
import shutil
from pathlib import Path
from typing import Dict, Any
import importlib.util


class ManimRenderer:
    """Renders Manim scenes programmatically."""

    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.generated_dir = self.base_dir / "generated"
        self.generated_dir.mkdir(exist_ok=True)

        # Configure Manim to use imageio-ffmpeg
        try:
            import imageio_ffmpeg
            from manim import config
            config.ffmpeg_executable = imageio_ffmpeg.get_ffmpeg_exe()
            print(f"Configured ffmpeg: {config.ffmpeg_executable}")
        except Exception as e:
            print(f"Warning: Could not configure ffmpeg: {e}")

    async def render(self, scene_path: Path) -> Dict[str, Any]:
        """
        Render a Manim scene programmatically.
        """
        try:
            if not scene_path.exists():
                return {
                    "status": "error",
                    "error": f"Scene file not found: {scene_path}"
                }

            # Extract scene class name
            scene_code = scene_path.read_text()
            scene_class_name = self._extract_scene_class(scene_code)

            if not scene_class_name:
                return {
                    "status": "error",
                    "error": "Could not find Scene class in code"
                }

            # Prepare output directory
            media_dir = self.generated_dir / "media"
            self._safe_remove_tree(media_dir)
            media_dir.mkdir(exist_ok=True)

            print(f"\nRendering scene: {scene_class_name}")

            # Import and render
            try:
                import imageio_ffmpeg
                from manim import config, tempconfig

                ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
                print(f"Using ffmpeg: {ffmpeg_path}")

                # Load the scene module
                spec = importlib.util.spec_from_file_location("generated_scene", scene_path)
                scene_module = importlib.util.module_from_spec(spec)
                sys.modules["generated_scene"] = scene_module
                spec.loader.exec_module(scene_module)

                # Get the scene class
                scene_class = getattr(scene_module, scene_class_name)

                # Render with configuration
                with tempconfig({
                    "ffmpeg_executable": ffmpeg_path,
                    "quality": "medium_quality",
                    "disable_caching": True,
                    "output_file": "output",
                    "media_dir": str(media_dir)
                }):
                    scene = scene_class()
                    scene.render()

                print("Rendering complete")

                # Find the generated video
                output_video = None
                for video_file in media_dir.rglob("*.mp4"):
                    # Skip partial movie files
                    if "partial_movie_files" not in str(video_file):
                        output_video = video_file
                        break

                if not output_video or not output_video.exists():
                    return {
                        "status": "error",
                        "error": "Video file not found after rendering"
                    }

                # Copy to latest.mp4
                latest_video = self.generated_dir / "latest.mp4"
                if not self._safe_copy(output_video, latest_video):
                    return {
                        "status": "error",
                        "error": "Failed to copy video file"
                    }

                print(f"Video saved: {latest_video}")

                # Cleanup
                if "generated_scene" in sys.modules:
                    del sys.modules["generated_scene"]

                return {
                    "status": "success",
                    "video_path": latest_video
                }

            except Exception as e:
                import traceback
                error_trace = traceback.format_exc()
                return {
                    "status": "error",
                    "error": f"Rendering error: {str(e)}\n\n{error_trace}"
                }

        except Exception as e:
            return {
                "status": "error",
                "error": f"Error: {str(e)}"
            }

    def _safe_remove_tree(self, path: Path, max_retries: int = 3) -> bool:
        """Safely remove directory tree, handling Windows file locks."""
        for attempt in range(max_retries):
            try:
                if path.exists():
                    shutil.rmtree(path)
                return True
            except PermissionError as e:
                if attempt < max_retries - 1:
                    print(f"Warning: Failed to delete {path}, retrying... ({e})")
                    time.sleep(0.5)
                else:
                    print(f"Warning: Could not delete {path} (file may be in use). Continuing...")
                    return False
            except Exception as e:
                print(f"Warning: Error deleting {path}: {e}")
                return False
        return False

    def _safe_copy(self, src: Path, dst: Path, max_retries: int = 3) -> bool:
        """Safely copy file, handling Windows file locks."""
        for attempt in range(max_retries):
            try:
                if dst.exists():
                    dst.unlink()
                shutil.copy(src, dst)
                return True
            except PermissionError as e:
                if attempt < max_retries - 1:
                    print(f"Warning: Failed to copy to {dst}, retrying... ({e})")
                    time.sleep(0.5)
                else:
                    print(f"Error: Could not copy video file: {e}")
                    return False
            except Exception as e:
                print(f"Error copying file: {e}")
                return False
        return False

    def _extract_scene_class(self, code: str) -> str:
        """Extract the Scene class name from code."""
        import re
        match = re.search(r'class\s+(\w+)\s*\(\s*Scene\s*\)', code)
        if match:
            return match.group(1)
        return None
