"""Sistema de EDOs da equação geodésica: d^2x^mu/dl^2 + Gamma^mu_ab u^a u^b = 0."""

import os
import pickle
import numpy as np

from .christoffel import compute_christoffel, lambdify_christoffel

_CACHE_PATH = os.path.join(os.path.dirname(__file__), '_christoffel_cache.pkl')


def get_christoffel_funcs():
    """Calcula (ou carrega do cache) as funções numéricas dos Christoffel."""
    if os.path.exists(_CACHE_PATH):
        with open(_CACHE_PATH, 'rb') as f:
            Gamma_expr, coords, M = pickle.load(f)
    else:
        Gamma_expr, coords, M = compute_christoffel()
        with open(_CACHE_PATH, 'wb') as f:
            pickle.dump((Gamma_expr, coords, M), f)

    return lambdify_christoffel(Gamma_expr, coords, M)


class GeodesicSystem:
    """Encapsula o campo vetorial da geodésica para uso com solve_ivp."""

    def __init__(self, mass=1.0):
        self.mass = mass
        self.gamma_funcs = get_christoffel_funcs()

    def rhs(self, lam, y):
        """y = [t, r, theta, phi, u^t, u^r, u^theta, u^phi]."""
        r, theta = y[1], y[2]
        u = y[4:8]

        du = np.zeros(4)
        for (mu, alpha, beta), func in self.gamma_funcs.items():
            du[mu] -= func(r, theta, self.mass) * u[alpha] * u[beta]

        return np.concatenate([u, du])

    def normalization(self, y):
        """g_{mu nu} u^mu u^nu: deve ser -1 (massiva) ou 0 (fóton)."""
        r, theta = y[1], y[2]
        f = 1 - 2 * self.mass / r
        u_t, u_r, u_th, u_ph = y[4:8]

        return (
            -f * u_t**2
            + (1 / f) * u_r**2
            + r**2 * u_th**2
            + r**2 * np.sin(theta)**2 * u_ph**2
        )
