"""Backward ray tracing in Schwarzschild spacetime (G=c=1)."""

from .camera import Camera
from .integrator import RayResult, trace_rays
from .renderer import render

__all__ = ["Camera", "RayResult", "trace_rays", "render"]
