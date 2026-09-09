"""
2D camera system for the black-hole renderer.

The camera is responsible only for deciding what region of the
simulation is visible.

It does not modify the physical coordinates of the simulation.
"""

import numpy as np


class Camera2D:
    """
    Simple 2D camera.

    Parameters
    ----------
    scale : float
        Half-width of the visible region.

    center_x : float
        Camera center in x.

    center_y : float
        Camera center in y.
    """

    def __init__(
        self,
        scale=10.0,
        center_x=0.0,
        center_y=0.0
    ):

        if scale <= 0:
            raise ValueError(
                "Camera scale must be greater than zero."
            )

        self.scale = float(scale)

        self.center_x = float(center_x)
        self.center_y = float(center_y)

    # ========================================================
    # Limits
    # ========================================================

    def limits(self):
        """
        Return current camera limits.

        Returns
        -------
        xmin, xmax, ymin, ymax
        """

        xmin = self.center_x - self.scale
        xmax = self.center_x + self.scale

        ymin = self.center_y - self.scale
        ymax = self.center_y + self.scale

        return xmin, xmax, ymin, ymax

    # ========================================================
    # Apply camera
    # ========================================================

    def apply(self, ax):
        """
        Apply camera limits to a Matplotlib axis.

        Parameters
        ----------
        ax : matplotlib.axes.Axes
            Axis where the camera should be applied.
        """

        xmin, xmax, ymin, ymax = self.limits()

        ax.set_xlim(xmin, xmax)
        ax.set_ylim(ymin, ymax)

    # ========================================================
    # Zoom
    # ========================================================

    def zoom(self, factor):
        """
        Zoom the camera.

        factor < 1  -> zoom in
        factor > 1  -> zoom out
        """

        if factor <= 0:
            raise ValueError(
                "Zoom factor must be greater than zero."
            )

        self.scale *= factor

    def zoom_in(self, factor=0.8):
        """
        Zoom in.
        """

        self.zoom(factor)

    def zoom_out(self, factor=1.25):
        """
        Zoom out.
        """

        self.zoom(factor)

    # ========================================================
    # Pan
    # ========================================================

    def pan(self, dx, dy):
        """
        Move the camera.

        Parameters
        ----------
        dx : float
            Horizontal displacement.

        dy : float
            Vertical displacement.
        """

        self.center_x += dx
        self.center_y += dy

    # ========================================================
    # Center
    # ========================================================

    def set_center(self, x, y):
        """
        Set camera center.
        """

        self.center_x = float(x)
        self.center_y = float(y)

    # ========================================================
    # Automatic framing
    # ========================================================

    def fit_to_data(
        self,
        x,
        y,
        margin=1.10,
        minimum_scale=1.0
    ):
        """
        Automatically adjust the camera to contain data.

        Parameters
        ----------
        x : ndarray
            x coordinates.

        y : ndarray
            y coordinates.

        margin : float
            Additional margin around the data.

        minimum_scale : float
            Minimum camera scale.
        """

        x = np.asarray(x)
        y = np.asarray(y)

        if x.size == 0 or y.size == 0:
            return

        xmin = np.min(x)
        xmax = np.max(x)

        ymin = np.min(y)
        ymax = np.max(y)

        center_x = (xmin + xmax) / 2.0
        center_y = (ymin + ymax) / 2.0

        width = xmax - xmin
        height = ymax - ymin

        scale = max(width, height) / 2.0

        scale *= margin

        scale = max(
            scale,
            minimum_scale
        )

        self.center_x = center_x
        self.center_y = center_y

        self.scale = scale