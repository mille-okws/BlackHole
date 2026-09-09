"""Integração numérica das geodésicas com scipy.solve_ivp."""

import numpy as np
from scipy.integrate import solve_ivp

from physics.geodesic import GeodesicSystem
from .events import make_capture_event, make_escape_event


def integrate_geodesic(y0, lam_span, mass=1.0, r_capture_factor=1.001,
                        r_max=100.0, max_step=0.5, rtol=1e-9, atol=1e-11):
    """Integra uma geodésica até captura, escape, ou fim do intervalo.

    Retorna o objeto de solução do solve_ivp (sol.y, sol.t, sol.t_events...).
    """
    system = GeodesicSystem(mass=mass)

    events = [
        make_capture_event(mass, r_capture_factor),
        make_escape_event(r_max),
    ]

    sol = solve_ivp(
        system.rhs,
        lam_span,
        y0,
        method='DOP853',
        max_step=max_step,
        rtol=rtol,
        atol=atol,
        events=events,
        dense_output=True,
    )

    sol.system = system
    return sol


def check_normalization_drift(sol, mass=1.0):
    """Retorna array com g_uv u^u u^v ao longo da trajetória (invariante numérico)."""
    system = GeodesicSystem(mass=mass) if not hasattr(sol, 'system') else sol.system
    return np.array([system.normalization(sol.y[:, i]) for i in range(sol.y.shape[1])])
