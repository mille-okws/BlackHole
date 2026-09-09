"""Teste 1 (M->0, espaço plano) e Teste 2 (limite newtoniano, r >> 2M)."""

import numpy as np
from physics.initial_conditions import massive_equatorial
from simulation.integrator import integrate_geodesic


def test_flat_space():
    """Com M ~ 0, a trajetória deve ser aproximadamente retilínea (u^phi ~ const, r cresce linear)."""
    mass = 1e-6
    y0 = massive_equatorial(r0=50.0, phi0=0.0, u_r0=0.1, u_phi0=0.0, mass=mass)

    sol = integrate_geodesic(y0, (0, 100), mass=mass, r_max=1000.0)

    r_vals = sol.y[1]
    dr_dlam = np.diff(r_vals) / np.diff(sol.t)
    ok = np.allclose(dr_dlam, dr_dlam[0], atol=1e-3)

    print(f"[Teste 1] Espaço plano (M->0): dr aprox. constante = {ok}")
    return ok


def test_newtonian_limit():
    """Para r >> 2M, ddot(r) deve se aproximar de -M/r^2 (aceleração newtoniana radial)."""
    mass = 1.0
    r0 = 1000.0
    y0 = massive_equatorial(r0=r0, phi0=0.0, u_r0=0.0, u_phi0=0.0, mass=mass)

    sol = integrate_geodesic(y0, (0, 5), mass=mass, r_max=r0 * 2)

    dlam = 0.01
    lam_eval = np.array([0.0, dlam, 2 * dlam])
    r_vals = sol.sol(lam_eval)[1]
    ddr_numeric = (r_vals[2] - 2 * r_vals[1] + r_vals[0]) / dlam**2
    ddr_expected = -mass / r0**2

    rel_error = abs(ddr_numeric - ddr_expected) / abs(ddr_expected)
    ok = rel_error < 0.05

    print(f"[Teste 2] Limite newtoniano: erro relativo = {rel_error:.4f}, ok = {ok}")
    return ok


if __name__ == '__main__':
    test_flat_space()
    test_newtonian_limit()
