"""Vectorized exact spatial null-geodesic equations for Schwarzschild.

Spherical symmetry confines each ray to an orbital plane. With affine
parameter lambda, L=|x cross x'| is conserved and the exact equation is
x'' = -3 M L**2 x/r**5 (not a Newtonian approximation). It is equivalent
to r''=L**2/r**3-3*M*L**2/r**4, phi'=L/r**2, and the existing Christoffel
equations. Time is unnecessary for tracing a static background.
"""

from dataclasses import dataclass

import numpy as np
from scipy.integrate import solve_ivp


@dataclass
class RayResult:
    directions: np.ndarray
    captured: np.ndarray
    escaped: np.ndarray
    positions: np.ndarray
    velocities: np.ndarray
    energy_error: np.ndarray
    steps: int

    @property
    def unresolved(self):
        return ~(self.captured | self.escaped)


def trace_rays(positions, velocities, mass=1.0, escape_radius=200.0,
               step_fraction=0.035, max_steps=2000):
    """Integrate independent rays with radius-scaled RK4 affine steps.

    A ray is captured only after crossing 2.002M, and escaped only after
    crossing the outer sphere outwards. Step-budget exhaustion is retained
    as unresolved, never painted black as if it were physical capture.
    Escape directions are evaluated at a finite radius, approximating the
    asymptotic celestial sky. Increase escape_radius to check that error.
    """
    x = np.array(positions, dtype=float, copy=True)
    v = np.array(velocities, dtype=float, copy=True)
    if x.ndim != 2 or x.shape[1] != 3 or v.shape != x.shape or not len(x):
        raise ValueError("As posições e velocidades devem ter formato (N, 3), N > 0.")
    if not np.all(np.isfinite(x)) or not np.all(np.isfinite(v)):
        raise ValueError("Os raios devem conter apenas valores finitos.")
    if not np.isfinite(mass) or mass < 0:
        raise ValueError("A massa deve ser finita e não negativa.")
    if not np.isfinite(step_fraction) or not 0 < step_fraction <= 0.2:
        raise ValueError("step_fraction deve estar entre 0 e 0.2.")
    if not isinstance(max_steps, int) or isinstance(max_steps, bool) or max_steps < 1:
        raise ValueError("max_steps deve ser inteiro positivo.")
    radius = np.linalg.norm(x, axis=1)
    if np.any(radius <= 2.002 * mass) or np.any(radius == 0):
        raise ValueError("Os raios devem começar fora do horizonte de captura.")
    if not np.isfinite(escape_radius) or escape_radius <= radius.max():
        raise ValueError("O raio de escape deve exceder todas as posições iniciais.")
    if np.any(np.linalg.norm(v, axis=1) == 0):
        raise ValueError("A velocidade de um raio não pode ser zero.")

    angular_squared = np.sum(np.cross(x, v) ** 2, axis=1)
    energy_squared = np.sum(v * v, axis=1) - 2 * mass * angular_squared / radius**3
    if np.any(energy_squared <= 0):
        raise ValueError("Os raios devem ter energia nula-geodésica real positiva.")
    captured = np.zeros(len(x), dtype=bool)
    escaped = np.zeros(len(x), dtype=bool)

    if mass == 0:
        # A radial flat-space ray crosses the origin. Radius-scaled steps
        # alone would approach r=0 forever, so solve this exact straight line.
        speed_squared = np.sum(v * v, axis=1)
        dot = np.sum(x * v, axis=1)
        affine = (-dot + np.sqrt(dot**2 + speed_squared
                                * (escape_radius**2 - radius**2))) / speed_squared
        x += affine[:, None] * v
        directions = v / np.sqrt(speed_squared)[:, None]
        return RayResult(directions, captured, ~captured, x, v, np.zeros(len(x)), 0)

    # Near the unstable photon orbit, tiny trajectory errors are strongly
    # amplified. Select a higher-accuracy solver using b, but still decide
    # capture/escape ONLY by integrated horizon/outer-sphere events.
    impact = np.sqrt(angular_squared / energy_squared)
    proximity = np.abs(impact / (3 * np.sqrt(3) * mass) - 1)
    precise = proximity < 1e-4
    for index in np.flatnonzero(precise):
        # At machine precision of the separatrix, no finite-precision claim
        # of capture or escape is reliable. Keep such rays unresolved.
        if proximity[index] < 1e-12:
            continue
        coefficient = -3 * mass * angular_squared[index]

        def rhs(affine, state):
            point = state[:3]
            acceleration = coefficient * point / np.linalg.norm(point)**5
            return np.concatenate((state[3:], acceleration))

        def horizon(affine, state):
            return np.linalg.norm(state[:3]) - 2.002 * mass

        def outer(affine, state):
            return np.linalg.norm(state[:3]) - escape_radius

        horizon.terminal, horizon.direction = True, -1
        outer.terminal, outer.direction = True, 1
        energy = np.sqrt(energy_squared[index])
        budget = max_steps * step_fraction * radius[index] / energy
        solution = solve_ivp(
            rhs, (0, budget), np.concatenate((x[index], v[index])),
            method="DOP853", rtol=2e-13, atol=2e-14,
            max_step=mass / energy, events=(horizon, outer),
        )
        if not solution.success:
            raise RuntimeError(f"Integração adaptativa falhou: {solution.message}")
        x[index], v[index] = solution.y[:3, -1], solution.y[3:, -1]
        captured[index] = bool(solution.t_events[0].size)
        escaped[index] = bool(solution.t_events[1].size)

    for step in range(max_steps):
        indices = np.flatnonzero(~(captured | escaped | precise))
        if not indices.size:
            break
        p, q = x[indices], v[indices]
        h = (step_fraction * np.linalg.norm(p, axis=1)
             / np.linalg.norm(q, axis=1))[:, None]
        coefficient = (-3 * mass * angular_squared[indices])[:, None]

        def acceleration(point):
            return coefficient * point / np.linalg.norm(point, axis=1)[:, None]**5

        a1 = acceleration(p)
        q2 = q + h * a1 / 2
        a2 = acceleration(p + h * q / 2)
        q3 = q + h * a2 / 2
        a3 = acceleration(p + h * q2 / 2)
        q4 = q + h * a3
        a4 = acceleration(p + h * q3)
        x[indices] = p + h * (q + 2 * q2 + 2 * q3 + q4) / 6
        v[indices] = q + h * (a1 + 2 * a2 + 2 * a3 + a4) / 6
        radius = np.linalg.norm(x[indices], axis=1)
        if not np.all(np.isfinite(radius)) or not np.all(np.isfinite(v[indices])):
            raise RuntimeError("A integração dos raios produziu valores não finitos.")
        captured[indices] = (mass > 0) & (radius <= 2.002 * mass)
        escaped[indices] = ((radius >= escape_radius)
                            & (np.sum(x[indices] * v[indices], axis=1) > 0))

    radius = np.linalg.norm(x, axis=1)
    energy_final = np.sum(v * v, axis=1) - 2 * mass * angular_squared / radius**3
    error = np.abs(energy_final - energy_squared) / energy_squared
    directions = np.zeros_like(v)
    directions[escaped] = v[escaped] / np.linalg.norm(v[escaped], axis=1, keepdims=True)
    return RayResult(directions, captured, escaped, x, v, error, step + 1)
