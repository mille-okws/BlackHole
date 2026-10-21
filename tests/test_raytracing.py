"""Independent physical and numerical checks of backward Schwarzschild rays."""

import unittest

import numpy as np

from physics.initial_conditions import photon_equatorial
from raytracing import Camera, render, trace_rays
from simulation.integrator import integrate_geodesic


def impact_rays(impacts, distance=30.0, mass=1.0):
    impacts = np.asarray(impacts, dtype=float)
    f = 1 - 2 * mass / distance
    transverse = impacts * np.sqrt(f) / distance
    positions = np.zeros((impacts.size, 3))
    positions[:, 0] = distance
    velocities = np.zeros_like(positions)
    velocities[:, 0] = -np.sqrt(f) * np.sqrt(1 - transverse**2)
    velocities[:, 1] = transverse
    return positions, velocities


class CameraTests(unittest.TestCase):
    def test_camera_emits_null_initial_conditions_in_static_tetrad(self):
        camera = Camera(width=7, height=5)
        positions, velocities = camera.rays()
        radius = np.linalg.norm(positions, axis=1)
        angular_squared = np.sum(np.cross(positions, velocities)**2, axis=1)
        energy_squared = np.sum(velocities**2, axis=1) - 2 * angular_squared / radius**3
        np.testing.assert_allclose(energy_squared, 1 - 2 / camera.distance, atol=1e-14)
        np.testing.assert_array_equal(velocities[17, 1:], [0, 0])

    def test_rejects_invalid_camera(self):
        for options in ({"width": 0}, {"height": 2.5}, {"fov": 180},
                        {"distance": 2}, {"mass": -1}, {"distance": float("nan")}):
            with self.subTest(options=options), self.assertRaises(ValueError):
                Camera(**options)


class GeodesicTests(unittest.TestCase):
    def test_flat_spacetime_is_straight_and_has_no_shadow(self):
        camera = Camera(width=9, height=7, mass=0)
        positions, velocities = camera.rays()
        result = trace_rays(positions, velocities, mass=0)
        self.assertTrue(result.escaped.all())
        self.assertFalse(result.captured.any())
        np.testing.assert_allclose(result.directions, velocities, atol=1e-13)

    def test_critical_impact_parameter_separates_capture_from_escape(self):
        critical = 3 * np.sqrt(3)
        positions, velocities = impact_rays([0, critical * 0.999, critical * 1.001, 8])
        result = trace_rays(positions, velocities)
        np.testing.assert_array_equal(result.captured, [True, True, False, False])
        np.testing.assert_array_equal(result.escaped, [False, False, True, True])
        self.assertLess(result.energy_error.max(), 1e-5)

    def test_agrees_with_existing_full_christoffel_integrator(self):
        positions, velocities = impact_rays([6.0])
        v = velocities[0]
        state = photon_equatorial(30.0, 0, v[0], v[1] / 30)
        solution = integrate_geodesic(state, (0, 1000), r_max=200)
        self.assertTrue(solution.success, solution.message)
        self.assertEqual(len(solution.t_events[1]), 1)
        _, radius, _, phi, _, radial, _, angular = solution.y[:, -1]
        expected = np.array([
            radial * np.cos(phi) - radius * angular * np.sin(phi),
            radial * np.sin(phi) + radius * angular * np.cos(phi), 0,
        ])
        expected /= np.linalg.norm(expected)
        result = trace_rays(positions, velocities)
        self.assertTrue(result.escaped[0])
        np.testing.assert_allclose(result.directions[0], expected, atol=2e-5)

    def test_extremely_near_critical_escape_is_not_falsely_captured(self):
        critical = 3 * np.sqrt(3)
        positions, velocities = impact_rays(
            [critical * (1 - 1e-8), critical * (1 + 1e-8), critical], distance=20,
        )
        result = trace_rays(positions, velocities)
        np.testing.assert_array_equal(result.captured, [True, False, False])
        np.testing.assert_array_equal(result.escaped, [False, True, False])
        np.testing.assert_array_equal(result.unresolved, [False, False, True])

    def test_weak_field_deflection_approaches_four_mass_over_impact(self):
        positions, velocities = impact_rays([100.0], distance=10000)
        result = trace_rays(positions, velocities, escape_radius=20000)
        initial = velocities[0] / np.linalg.norm(velocities[0])
        angle = np.arccos(np.clip(initial @ result.directions[0], -1, 1))
        self.assertAlmostEqual(angle, 4 / 100, delta=0.002)

    def test_step_refinement_and_outer_boundary_converge(self):
        positions, velocities = impact_rays([5.25, 6, 8])
        coarse = trace_rays(positions, velocities)
        fine = trace_rays(positions, velocities, step_fraction=0.0175)
        farther = trace_rays(positions, velocities, escape_radius=400)
        self.assertTrue(coarse.escaped.all())
        np.testing.assert_allclose(coarse.directions, fine.directions, atol=3e-5)
        np.testing.assert_allclose(coarse.directions, farther.directions, atol=3e-5)
        self.assertLess(fine.energy_error.max(), coarse.energy_error.max())

    def test_step_budget_exhaustion_is_not_capture(self):
        positions, velocities = impact_rays([0, 6])
        result = trace_rays(positions, velocities, max_steps=1)
        self.assertTrue(result.unresolved.all())
        self.assertFalse(result.captured.any())
        with self.assertRaisesRegex(RuntimeError, "não convergiram"):
            render(Camera(width=3, height=3), max_steps=1)


class ImageTests(unittest.TestCase):
    def test_shadow_matches_finite_observer_angular_radius(self):
        camera = Camera(width=65, height=65)
        positions, velocities = camera.rays()
        radius = np.linalg.norm(positions, axis=1)
        angular = np.linalg.norm(np.cross(positions, velocities), axis=1)
        expected_capture = angular / np.sqrt(1 - 2 / radius) < 3 * np.sqrt(3)
        image, result = render(camera)
        self.assertFalse(result.unresolved.any())
        np.testing.assert_array_equal(result.captured, expected_capture)
        self.assertTrue(np.all(image.reshape(-1, 3)[result.captured] == 0))
        self.assertTrue(np.all(image.reshape(-1, 3)[result.escaped] > 0))
        self.assertTrue(np.isfinite(image).all())
        mask = result.captured.reshape(65, 65)
        np.testing.assert_array_equal(mask, mask[::-1, :])
        np.testing.assert_array_equal(mask, mask[:, ::-1])

    def test_mass_and_length_rescaling_preserve_the_image(self):
        original, a = render(Camera(width=17, height=13))
        scaled, b = render(Camera(width=17, height=13, distance=60, mass=2))
        np.testing.assert_array_equal(a.captured, b.captured)
        np.testing.assert_allclose(original, scaled, atol=1e-11)


if __name__ == "__main__":
    unittest.main()
