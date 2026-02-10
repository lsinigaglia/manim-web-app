#!/usr/bin/env python3
"""
Simple test to verify Manim works directly (no Docker).
"""
import subprocess
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

def test_manim():
    """Test Manim rendering directly."""
    print("="*60)
    print("Testing Manim (Direct)")
    print("="*60)

    # Write test scene
    scene_path = GENERATED_DIR / "scene.py"
    scene_path.write_text(TEST_SCENE)
    print(f"[OK] Created test scene: {scene_path}")

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
            print(f"[FAIL] Rendering failed:")
            print(result.stderr or result.stdout)
            return False

        print("[OK] Rendering completed")
        print(result.stdout)

        # Find video
        media_dir = GENERATED_DIR / "media"
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
            print(f"\n[OK] Video created: {output_video} ({size} bytes)")

            print("\n" + "="*60)
            print("[PASS] Manim test PASSED")
            print("="*60)
            return True
        else:
            print("[FAIL] Video file not found")
            return False

    except Exception as e:
        print(f"[FAIL] Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_manim()
    exit(0 if success else 1)
