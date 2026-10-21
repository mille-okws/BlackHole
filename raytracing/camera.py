"""Pinhole camera in a static observer's local orthonormal frame."""

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class Camera:
    width: int = 640
    height: int = 400
    fov: float = 45.0  # vertical field of view, degrees
    distance: float = 30.0
    mass: float = 1.0

    def __post_init__(self):
        if any(isinstance(n, bool) or not isinstance(n, int) or n < 1
               for n in (self.width, self.height)):
            raise ValueError("A resolução deve conter inteiros positivos.")
        if not all(np.isfinite(v) for v in (self.fov, self.distance, self.mass)):
            raise ValueError("Os parâmetros da câmera devem ser finitos.")
        if not 0 < self.fov < 170:
            raise ValueError("O campo de visão deve estar entre 0 e 170 graus.")
        if self.mass < 0 or self.distance <= 2 * self.mass:
            raise ValueError("A câmera estática deve estar fora do horizonte (r > 2M).")

    def rays(self):
        """Return flattened positions/affine velocities for pixel-center rays.

        The camera lies on +x and looks toward the origin. Its screen axes
        are +y (right), +z (up). Local photon frequency is set to one;
        dr/dlambda=sqrt(f)*n_radial while transverse speeds equal n_local.
        By time-reversal symmetry these inward rays trace incoming light
        backwards; the resulting escape direction locates the source sky.
        """
        half_height = np.tan(np.deg2rad(self.fov) / 2)
        sx = (2 * (np.arange(self.width) + 0.5) / self.width - 1)
        sy = (1 - 2 * (np.arange(self.height) + 0.5) / self.height)
        xx, yy = np.meshgrid(sx * half_height * self.width / self.height,
                             sy * half_height)
        directions = np.stack((-np.ones_like(xx), xx, yy), axis=-1).reshape(-1, 3)
        directions /= np.linalg.norm(directions, axis=1, keepdims=True)
        velocities = directions.copy()
        velocities[:, 0] *= np.sqrt(1 - 2 * self.mass / self.distance)
        positions = np.zeros_like(velocities)
        positions[:, 0] = self.distance
        return positions, velocities
