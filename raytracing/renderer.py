"""Form the image from numerical geodesic outcomes and celestial radiance."""

import numpy as np

from .background import sample_sky
from .integrator import trace_rays


def render(camera, **integration_options):
    positions, velocities = camera.rays()
    options = {"escape_radius": max(200 * camera.mass, 4 * camera.distance)}
    options.update(integration_options)
    result = trace_rays(positions, velocities, mass=camera.mass, **options)
    unresolved = np.count_nonzero(result.unresolved)
    if unresolved:
        raise RuntimeError(
            f"{unresolved} raios não convergiram; aumente max_steps ou revise a integração."
        )
    rgb = np.zeros((len(positions), 3), dtype=float)
    rgb[result.escaped] = sample_sky(result.directions[result.escaped])
    return rgb.reshape(camera.height, camera.width, 3), result
