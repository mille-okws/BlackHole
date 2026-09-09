"""Teste 4: fóton em órbita circular instável deve permanecer próximo de r = 3M."""

import numpy as np
from physics.constants import R_PHOTON_SPHERE
from physics.initial_conditions import photon_sphere_state
from simulation.integrator import integrate_geodesic


def test_photon_sphere(mass=1.0):
    y0 = photon_sphere_state(mass=mass)

    sol = integrate_geodesic(y0, (0, 30), mass=mass, r_max=50.0)

    r_vals = sol.y[1]
    max_dev = np.max(np.abs(r_vals - R_PHOTON_SPHERE * mass))
    ok = max_dev < 0.5  # órbita instável: pequeno desvio numérico esperado, mas deve permanecer perto

    print(f"[Teste 4] Esfera de fótons: desvio máx. de 3M = {max_dev:.4f}, ok={ok}")
    return ok


if __name__ == '__main__':
    test_photon_sphere()
