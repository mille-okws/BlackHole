"""Eventos para solve_ivp: captura pelo horizonte, escape, e passagem por periélio."""


def make_capture_event(mass, factor=1.001):
    """Dispara quando r <= (1 + eps) * r_s (captura pelo buraco negro)."""
    r_s = 2.0 * mass

    def event(lam, y):
        return y[1] - factor * r_s

    event.terminal = True
    event.direction = -1
    return event


def make_escape_event(r_max):
    """Dispara quando r > r_max (partícula escapou para o infinito)."""

    def event(lam, y):
        return y[1] - r_max

    event.terminal = True
    event.direction = 1
    return event


def make_perihelion_event():
    """Dispara quando dr/dlambda = 0 (periélio ou afélio). Não termina a integração."""

    def event(lam, y):
        return y[5]  # u^r

    event.terminal = False
    event.direction = 0
    return event
