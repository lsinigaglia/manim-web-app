#!/usr/bin/env python3
"""
Test local Manim rendering with a simple "Hello Manim" scene.
Run this to verify Manim installation before starting the web app.
"""
import subprocess
import shutil
from pathlib import Path

BASE_DIR = Path(__file__).parent
GENERATED_DIR = BASE_DIR / "generated"
GENERATED_DIR.mkdir(exist_ok=True)

# Simple test scene
TEST_SCENE = '''from manim import *

class HelloManim(Scene):
    def construct(self):
        text = Text("Hello, Manim!", color=BLUE)
        self.play(Write(text))
        self.wait(1)
'''

def test_local_render():
    """Test local Manim rendering with a minimal scene."""
    print("="*60)
    print("Testing Local Manim Rendering")
    print("="*60)
    print()

    # Write test scene
    scene_path = GENERATED_DIR / "scene.py"
    scene_path.write_text(TEST_SCENE)
    print(f"✓ Created test scene: {scene_path}")

    # Prepare for render
    media_dir = GENERATED_DIR / "media"
    if media_dir.exists():
        shutil.rmtree(media_dir)
    media_dir.mkdir(exist_ok=True)

    # Render
    print("\nRendering scene...")
    cmd = [
        "manim",
        "-qm",
        "--disable_caching",
        "-o", "output",
        str(scene_path),
        "HelloManim"
    ]

    print(f"Command: {' '.join(cmd)}\n")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
            cwd=str(GENERATED_DIR)
        )

        if result.returncode != 0:
            print(f"✗ Rendering failed:")
            print(result.stderr or result.stdout)
            return False

        print("✓ Rendering completed")

        # Find video
        videos_dir = media_dir / "videos" / "scene" / "720p30"
        if not videos_dir.exists():
            videos_dir = media_dir / "videos" / "720p30"

        output_video = None
        if videos_dir.exists():
            for video_file in videos_dir.glob("*.mp4"):
                output_video = video_file
                break

        if output_video and output_video.exists():
            size = output_video.stat().st_size
            print(f"✓ Video created: {output_video} ({size} bytes)")

            # Copy to latest.mp4
            latest = GENERATED_DIR / "latest.mp4"
            shutil.copy(output_video, latest)
            print(f"✓ Copied to: {latest}")

            print("\n" + "="*60)
            print("✓ Local Manim rendering test PASSED")
            print("="*60)
            return True
        else:
            print("✗ Video file not found")
            return False

    except subprocess.TimeoutExpired:
        print("✗ Rendering timed out")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


if __name__ == "__main__":
    success = test_local_render()
    exit(0 if success else 1)
