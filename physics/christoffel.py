"""Símbolos de Christoffel gerados simbolicamente a partir da métrica."""

import sympy as sp
from .metric import get_metric, get_coords


def compute_christoffel():
    """Calcula Gamma^mu_{alpha beta} simbolicamente. Retorna array 4x4x4."""
    g, g_inv = get_metric()
    coords, M = get_coords()

    Gamma = sp.MutableDenseNDimArray.zeros(4, 4, 4)

    for mu in range(4):
        for alpha in range(4):
            for beta in range(4):
                expr = 0
                for nu in range(4):
                    expr += g_inv[mu, nu] * (
                        sp.diff(g[nu, alpha], coords[beta])
                        + sp.diff(g[nu, beta], coords[alpha])
                        - sp.diff(g[alpha, beta], coords[nu])
                    )
                Gamma[mu, alpha, beta] = sp.simplify(expr / 2)

    return Gamma, coords, M


def lambdify_christoffel(Gamma, coords, M):
    """Converte os símbolos não-nulos em funções numéricas rápidas (r, theta, M) -> valor."""
    r, theta = coords[1], coords[2]
    funcs = {}

    for mu in range(4):
        for alpha in range(4):
            for beta in range(4):
                expr = Gamma[mu, alpha, beta]
                if expr != 0:
                    funcs[(mu, alpha, beta)] = sp.lambdify(
                        (r, theta, M), expr, modules='numpy'
                    )
    return funcs
