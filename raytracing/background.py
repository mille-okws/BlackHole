"""Deterministic procedural celestial sky, independent of black-hole physics."""

from functools import lru_cache

import numpy as np
from scipy.ndimage import gaussian_filter, map_coordinates


@lru_cache(maxsize=1)
def _stars():
    rng = np.random.default_rng(12)
    texture = np.zeros((1024, 2048), dtype=np.float32)
    # Uniform solid-angle distribution rather than a concentration at poles.
    longitude = rng.uniform(0, 2 * np.pi, 12000)
    latitude = np.arcsin(rng.uniform(-1, 1, 12000))
    rows = ((0.5 - latitude / np.pi) * 1023).astype(int)
    cols = (longitude / (2 * np.pi) * 2048).astype(int) % 2048
    np.add.at(texture, (rows, cols), rng.pareto(1.8, 12000).clip(0, 12) + 0.25)
    return gaussian_filter(texture, sigma=0.65, mode=("nearest", "wrap"))


def sample_sky(directions):
    """Sample RGB radiance from unit outward directions; no painted shadow."""
    d = np.asarray(directions, dtype=float)
    longitude = np.mod(np.arctan2(d[:, 1], d[:, 0]), 2 * np.pi)
    latitude = np.arcsin(np.clip(d[:, 2], -1, 1))
    stars = map_coordinates(
        _stars(), [(0.5 - latitude / np.pi) * 1023,
                   longitude / (2 * np.pi) * 2048], order=1, mode="grid-wrap",
    )
    normal = np.array([0.25, 0.55, 0.8])
    normal /= np.linalg.norm(normal)
    band_angle = np.arcsin(np.clip(d @ normal, -1, 1))
    structure = (0.6 + 0.2 * np.sin(17 * d[:, 0] + 9 * d[:, 1])
                 + 0.2 * np.sin(31 * d[:, 2] - 13 * d[:, 0]))
    band = np.exp(-(band_angle / 0.16)**2) * structure
    dust = 1 - 0.75 * np.exp(-(band_angle / 0.025)**2)
    rgb = (np.array([0.012, 0.019, 0.035])
           + (band * dust)[:, None] * np.array([0.22, 0.15, 0.09])
           + stars[:, None] * np.array([0.65, 0.8, 1.0]))
    return np.clip(rgb, 0, 1)
