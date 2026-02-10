"""
Simple Manim test to verify everything works
"""
from manim import *

class SimpleTest(Scene):
    def construct(self):
        circle = Circle()
        self.play(Create(circle))
        self.wait()
