"""
Main entry point for the Schwarzschild black-hole simulation.

This module:

1. Runs the complete physical validation suite.
2. Creates the 2D renderer.
3. Displays the Schwarzschild black-hole geometry.

The physical model itself is implemented in the physics/
and simulation/ packages.

The renderer is responsible only for visualization.
"""

# ============================================================
# Validation
# ============================================================

from validation.newtonian_limit import (
    test_flat_space,
    test_newtonian_limit,
)

from validation.schwarzschild_radius import (
    test_event_horizon,
)

from validation.photon_sphere import (
    test_photon_sphere,
)

from validation.circular_orbits import (
    test_stable_circular_orbit,
    test_isco,
)

from validation.precession import (
    test_perihelion_precession,
)


# ============================================================
# Renderer
# ============================================================

from renderer import Renderer2D


# ============================================================
# Validation
# ============================================================

def run_validation():
    """
    Run the complete physical validation suite.

    Returns
    -------
    results : dict
        Dictionary containing the result of every test.
    """

    print("========================================")
    print(" Schwarzschild Black Hole Simulation")
    print("========================================")

    print("\n=== Validação física ===")

    results = {
        "flat_space": test_flat_space(),
        "newtonian_limit": test_newtonian_limit(),
        "event_horizon": test_event_horizon(),
        "photon_sphere": test_photon_sphere(),
        "circular_orbit": test_stable_circular_orbit(),
        "isco": test_isco(),
        "precession": test_perihelion_precession(),
    }

    print("\n=== Resumo ===")

    for name, ok in results.items():

        status = "OK" if ok else "FALHOU"

        print(
            f"{name}: {status}"
        )

    return results


# ============================================================
# Renderer
# ============================================================

def run_renderer():
    """
    Create and display the 2D Schwarzschild black hole.

    At this stage the renderer displays:

        - Event horizon: r = 2M
        - Photon sphere: r = 3M
        - ISCO: r = 6M

    Trajectories will be added when the simulation output
    is connected to the renderer.
    """

    print("\n=== Renderer 2D ===")

    renderer = Renderer2D(
        M=1.0
    )

    renderer.draw_scene(
        draw_horizon=True,
        draw_photon_sphere=True,
        draw_isco=True,
        draw_grid=True,
        draw_axes=True,
        draw_center=True,
        title="Schwarzschild Black Hole"
    )

    renderer.show()


# ============================================================
# Main
# ============================================================

def main():
    """
    Main execution flow.
    """

    # --------------------------------------------------------
    # 1. Run physical validation
    # --------------------------------------------------------

    results = run_validation()

    # --------------------------------------------------------
    # 2. Check validation
    # --------------------------------------------------------

    all_tests_passed = all(
        results.values()
    )

    if not all_tests_passed:

        print(
            "\n[ERRO] Uma ou mais validações falharam."
        )

        print(
            "[INFO] Renderer não será executado."
        )

        return

    # --------------------------------------------------------
    # 3. Validation successful
    # --------------------------------------------------------

    print(
        "\n[OK] Todos os testes físicos passaram."
    )

    # --------------------------------------------------------
    # 4. Start renderer
    # --------------------------------------------------------

    run_renderer()


# ============================================================
# Script entry point
# ============================================================

if __name__ == "__main__":
    main()