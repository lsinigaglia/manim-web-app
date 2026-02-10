"""
Test rendering with ffmpeg configured
"""
import imageio_ffmpeg
from manim import *

# Configure ffmpeg before anything else
config.ffmpeg_executable = imageio_ffmpeg.get_ffmpeg_exe()
print(f"Using ffmpeg: {config.ffmpeg_executable}")

class SimpleTest(Scene):
    def construct(self):
        circle = Circle()
        self.play(Create(circle))
        self.wait()

if __name__ == "__main__":
    # Render the scene
    scene = SimpleTest()
    scene.render()
