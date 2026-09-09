"""Métrica de Schwarzschild em coordenadas (t, r, theta, phi), unidades G=c=1."""

import sympy as sp

t, r, theta, phi, M = sp.symbols('t r theta phi M', positive=True)
coords = [t, r, theta, phi]


def get_metric():
    """Retorna tensor métrico g_{mu nu} e sua inversa, simbólicos."""
    f = 1 - 2 * M / r

    g = sp.diag(
        -f,
        1 / f,
        r**2,
        r**2 * sp.sin(theta)**2
    )

    g_inv = sp.simplify(g.inv())
    return g, g_inv


def get_coords():
    return coords, M
