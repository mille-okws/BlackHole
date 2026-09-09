"""Geração de condições iniciais (posição + 4-velocidade normalizada)."""

import numpy as np


def _f(r, mass):
    return 1 - 2 * mass / r


def massive_equatorial(r0, phi0, u_r0, u_phi0, mass=1.0):
    """Estado inicial de partícula massiva no plano equatorial (theta = pi/2).

    Resolve u^t a partir da normalização g_uv u^u u^v = -1.
    """
    theta0 = np.pi / 2
    f = _f(r0, mass)

    rhs = 1 + (1 / f) * u_r0**2 + r0**2 * u_phi0**2
    u_t0 = np.sqrt(rhs / f)

    return np.array([0.0, r0, theta0, phi0, u_t0, u_r0, 0.0, u_phi0])


def photon_equatorial(r0, phi0, u_r0, u_phi0, mass=1.0):
    """Estado inicial de fóton no plano equatorial. Resolve u^t com ds^2 = 0."""
    theta0 = np.pi / 2
    f = _f(r0, mass)

    rhs = (1 / f) * u_r0**2 + r0**2 * u_phi0**2
    u_t0 = np.sqrt(rhs / f)

    return np.array([0.0, r0, theta0, phi0, u_t0, u_r0, 0.0, u_phi0])


def circular_orbit_velocity(r0, mass=1.0):
    """u^phi = dphi/dtau para órbita circular de partícula massiva em r0 (requer r0 > 3M)."""
    omega = np.sqrt(mass / r0**3)  # dphi/dt, coincide com Kepler newtoniano
    u_t = 1.0 / np.sqrt(1 - 3 * mass / r0)
    return omega * u_t


def photon_sphere_state(mass=1.0, direction=1.0):
    """Fóton em órbita circular instável em r = 3M."""
    r0 = 3.0 * mass
    u_phi0 = direction * np.sqrt(1 / r0**3) * np.sqrt(mass)
    return photon_equatorial(r0, 0.0, 0.0, u_phi0, mass)
