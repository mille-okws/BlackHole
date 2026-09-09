"""Conversão de soluções de EDO em trajetórias utilizáveis (cartesianas, etc)."""

import numpy as np


def to_cartesian_equatorial(sol):
    """Converte (r, phi) do plano equatorial em coordenadas (x, y). Assume theta ~ pi/2."""
    r = sol.y[1]
    phi = sol.y[3]

    x = r * np.cos(phi)
    y = r * np.sin(phi)
    return x, y


def extract_r_min(sol):
    """Distância mínima de aproximação ao longo da trajetória."""
    return np.min(sol.y[1])


def extract_final_state(sol):
    """Último estado da trajetória e o motivo de parada (evento ou fim do span)."""
    reason = 'capture' if sol.t_events[0].size else (
        'escape' if sol.t_events[1].size else 'span_end'
    )
    return sol.y[:, -1], reason
