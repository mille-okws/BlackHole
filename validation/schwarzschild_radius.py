"""Teste 3: geodésica radial que cai deve ser capturada em r = 2M."""

from physics.initial_conditions import massive_equatorial
from simulation.integrator import integrate_geodesic
from simulation.trajectories import extract_final_state


def test_event_horizon(mass=1.0):
    """Partícula em queda radial pura deve disparar o evento de captura em r ~ 2M."""
    r0 = 10.0 * mass
    y0 = massive_equatorial(r0=r0, phi0=0.0, u_r0=-0.3, u_phi0=0.0, mass=mass)

    sol = integrate_geodesic(y0, (0, 200), mass=mass)
    final_state, reason = extract_final_state(sol)

    ok = reason == 'capture' and abs(final_state[1] - 2 * mass) < 0.05 * mass

    print(f"[Teste 3] Captura no horizonte: motivo={reason}, r_final={final_state[1]:.4f}, ok={ok}")
    return ok


if __name__ == '__main__':
    test_event_horizon()
