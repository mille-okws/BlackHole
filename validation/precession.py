"""Teste 6: avanço do periélio em órbita elíptica. Delta_phi = 6*pi*M / (a*(1-e^2))."""

import numpy as np
from scipy.signal import argrelextrema

from simulation.integrator import integrate_geodesic


def expected_precession(a, e, mass=1.0):
    return 6 * np.pi * mass / (a * (1 - e**2))


def _bound_orbit_state(r_peri, r_apo, mass=1.0):
    """Resolve L e E a partir dos pontos de retorno (u^r=0 em r_peri e r_apo)."""
    f_p = 1 - 2 * mass / r_peri
    f_a = 1 - 2 * mass / r_apo

    L2 = (2 * mass * (1 / r_apo - 1 / r_peri)) / (
        f_a / r_apo**2 - f_p / r_peri**2
    )
    E2 = f_p * (1 + L2 / r_peri**2)

    u_phi0 = np.sqrt(L2) / r_peri**2
    u_t0 = np.sqrt(E2) / f_p

    return np.array([0.0, r_peri, np.pi / 2, 0.0, u_t0, 0.0, 0.0, u_phi0])


def test_perihelion_precession(mass=1.0, r_peri=40.0, r_apo=100.0):
    """Estima o avanço do periélio numericamente e compara com a fórmula analítica.

    Nota: a fórmula linear é uma aproximação de campo fraco (r >> M); por isso
    usamos raios grandes em unidades de M para que a comparação seja válida.
    """
    a = (r_peri + r_apo) / 2
    e = (r_apo - r_peri) / (r_apo + r_peri)

    y0 = _bound_orbit_state(r_peri, r_apo, mass)

    sol = integrate_geodesic(y0, (0, 20000), mass=mass, r_max=r_apo * 1.5, max_step=0.5)

    r_vals = sol.y[1]
    phi_vals = sol.y[3]

    minima_idx = argrelextrema(r_vals, np.less)[0]
    if len(minima_idx) < 2:
        print("[Teste 6] Não há periélios suficientes na janela de integração.")
        return False

    delta_phi_numeric = phi_vals[minima_idx[1]] - phi_vals[minima_idx[0]] - 2 * np.pi
    delta_phi_expected = expected_precession(a, e, mass)

    rel_error = abs(delta_phi_numeric - delta_phi_expected) / abs(delta_phi_expected)
    ok = rel_error < 0.15  # fórmula é aproximação de campo fraco

    print(f"[Teste 6] Precessão: numérico={delta_phi_numeric:.6f}, "
          f"esperado={delta_phi_expected:.6f}, erro rel.={rel_error:.4f}, ok={ok}")
    return ok


if __name__ == '__main__':
    test_perihelion_precession()
