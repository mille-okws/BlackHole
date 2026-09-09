"""
Geometric transformations used by the 2D renderer.

The physics engine works primarily with spherical coordinates:

    (r, theta, phi)

The 2D renderer represents the equatorial plane using:

    (x, y)

For theta = pi/2:

    x = r cos(phi)
    y = r sin(phi)

All functions in this module are independent of the numerical
integration code.
"""

import numpy as np


def spherical_to_cartesian(r, phi):
    """
    Convert equatorial spherical coordinates to Cartesian coordinates.

    Parameters
    ----------
    r : float or ndarray
        Radial coordinate.

    phi : float or ndarray
        Azimuthal coordinate in radians.

    Returns
    -------
    x : float or ndarray
        Cartesian x coordinate.

    y : float or ndarray
        Cartesian y coordinate.
    """

    r = np.asarray(r)
    phi = np.asarray(phi)

    x = r * np.cos(phi)
    y = r * np.sin(phi)

    return x, y


def normalize_coordinates(x, y, M):
    """
    Normalize Cartesian coordinates by the black-hole mass.

    In geometric units, M is commonly used as the characteristic
    length scale.

    Parameters
    ----------
    x : float or ndarray
        Cartesian x coordinate.

    y : float or ndarray
        Cartesian y coordinate.

    M : float
        Black-hole mass parameter.

    Returns
    -------
    x_norm : float or ndarray
        x / M.

    y_norm : float or ndarray
        y / M.
    """

    if M <= 0:
        raise ValueError("M must be greater than zero.")

    return x / M, y / M


def radial_to_cartesian(r, phi, M=1.0):
    """
    Convert (r, phi) directly to normalized Cartesian coordinates.

    This is a convenience function combining:

        spherical_to_cartesian()
        normalize_coordinates()

    Parameters
    ----------
    r : float or ndarray
        Radial coordinate.

    phi : float or ndarray
        Azimuthal coordinate in radians.

    M : float
        Black-hole mass parameter.

    Returns
    -------
    x : float or ndarray
        Normalized x coordinate.

    y : float or ndarray
        Normalized y coordinate.
    """

    x, y = spherical_to_cartesian(r, phi)

    return normalize_coordinates(x, y, M)


def circular_coordinates(radius, n_points=500):
    """
    Generate Cartesian coordinates for a circular structure.

    Useful for plotting:

        - event horizon
        - photon sphere
        - ISCO
        - arbitrary circular reference surfaces

    Parameters
    ----------
    radius : float
        Circle radius.

    n_points : int
        Number of points used to approximate the circle.

    Returns
    -------
    x : ndarray
        x coordinates.

    y : ndarray
        y coordinates.
    """

    if radius <= 0:
        raise ValueError("radius must be greater than zero.")

    if n_points < 3:
        raise ValueError("n_points must be at least 3.")

    phi = np.linspace(
        0.0,
        2.0 * np.pi,
        n_points
    )

    x = radius * np.cos(phi)
    y = radius * np.sin(phi)

    return x, y