"""Constantes físicas em unidades geométricas (G = c = M = 1)."""

G_SI = 6.67430e-11
C_SI = 2.99792458e8

# Em unidades geométricas
G = 1.0
C = 1.0
M = 1.0

# Raio de Schwarzschild em unidades de M
R_S = 2.0 * G * M / C**2

# Raios notáveis (em M)
R_PHOTON_SPHERE = 3.0 * M
R_ISCO = 6.0 * M


def schwarzschild_radius_si(mass_kg: float) -> float:
    """Converte raio de Schwarzschild para SI dado massa em kg."""
    return 2.0 * G_SI * mass_kg / C_SI**2
