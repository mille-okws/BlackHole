"""
Renderer package for the black hole simulation.

This package contains only visualization-related components.
It must not contain physical models, numerical integration,
or simulation logic.
"""

from .renderer_2d import Renderer2D
from .camera import Camera2D
from .geometry import (
    spherical_to_cartesian,
    normalize_coordinates,
)

__all__ = [
    "Renderer2D",
    "Camera2D",
    "spherical_to_cartesian",
    "normalize_coordinates",
]