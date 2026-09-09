"""Teste 5: órbitas circulares de partículas massivas e a ISCO em r = 6M."""

import numpy as np
from physics.constants import R_ISCO
from physics.initial_conditions import massive_equatorial, circular_orbit_velocity
from simulation.integrator import integrate_geodesic


def test_stable_circular_orbit(mass=1.0, r0=10.0):
    """r0 > 6M: órbita circular deve permanecer estável (r aprox. constante)."""
    u_phi0 = circular_orbit_velocity(r0, mass)
    y0 = massive_equatorial(r0=r0, phi0=0.0, u_r0=0.0, u_phi0=u_phi0, mass=mass)

    sol = integrate_geodesic(y0, (0, 200), mass=mass, r_max=r0 * 3)

    r_vals = sol.y[1]
    max_dev = np.max(np.abs(r_vals - r0))
    ok = max_dev < 0.1 * r0

    print(f"[Teste 5a] Órbita circular estável em r={r0}M: desvio máx.={max_dev:.4f}, ok={ok}")
    return ok


def test_isco(mass=1.0):
    """Em r = 6M, a órbita circular deve estar no limiar da estabilidade."""
    r0 = R_ISCO * mass
    u_phi0 = circular_orbit_velocity(r0, mass)
    y0 = massive_equatorial(r0=r0, phi0=0.0, u_r0=0.0, u_phi0=u_phi0, mass=mass)

    sol = integrate_geodesic(y0, (0, 300), mass=mass, r_max=r0 * 3)

    r_vals = sol.y[1]
    max_dev = np.max(np.abs(r_vals - r0))
    ok = max_dev < 0.2 * r0

    print(f"[Teste 5b] ISCO em r=6M: desvio máx.={max_dev:.4f}, ok={ok}")
    return ok


if __name__ == '__main__':
    test_stable_circular_orbit()
    test_isco()
