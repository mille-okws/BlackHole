"""
2D renderer for the Schwarzschild black-hole simulation.

This module is responsible exclusively for visualization.

It receives physical quantities calculated elsewhere and renders:

    - event horizon
    - photon sphere
    - ISCO
    - geodesic trajectories
    - initial/final positions
    - coordinate axes
    - grid

No physics is calculated here.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle

from .geometry import (
    spherical_to_cartesian,
    circular_coordinates,
)

from .camera import Camera2D

from . import styles


class Renderer2D:
    """
    Renderer for a 2D Schwarzschild black-hole visualization.

    Parameters
    ----------
    M : float
        Black-hole mass parameter.

    camera : Camera2D, optional
        Camera object controlling the visible region.

    figsize : tuple
        Figure size.

    dpi : int
        Figure resolution.
    """

    def __init__(
        self,
        M=1.0,
        camera=None,
        figsize=styles.FIGURE_SIZE,
        dpi=styles.FIGURE_DPI
    ):

        if M <= 0:
            raise ValueError(
                "Black-hole mass M must be greater than zero."
            )

        self.M = float(M)

        # Camera
        if camera is None:

            camera = Camera2D(
                scale=10.0
            )

        self.camera = camera

        # Figure
        self.fig, self.ax = plt.subplots(
            figsize=figsize,
            dpi=dpi
        )

        self.fig.patch.set_facecolor(
            styles.BACKGROUND_COLOR
        )

        self.ax.set_facecolor(
            styles.AXES_BACKGROUND_COLOR
        )

        # Objects created by renderer
        self.horizon = None
        self.photon_sphere = None
        self.isco = None

    # ========================================================
    # Event horizon
    # ========================================================

    def draw_black_hole(self):
        """
        Draw the event horizon.

        For Schwarzschild:

            r_h = 2M
        """

        radius = 2.0 * self.M

        self.horizon = Circle(
            (0.0, 0.0),
            radius,
            facecolor=styles.HORIZON_COLOR,
            edgecolor=styles.HORIZON_EDGE_COLOR,
            linewidth=styles.HORIZON_LINEWIDTH,
            zorder=10
        )

        self.ax.add_patch(
            self.horizon
        )

    # ========================================================
    # Photon sphere
    # ========================================================

    def draw_photon_sphere(self):
        """
        Draw the photon sphere.

        For Schwarzschild:

            r_ph = 3M
        """

        radius = 3.0 * self.M

        self.photon_sphere = Circle(
            (0.0, 0.0),
            radius,
            fill=False,
            edgecolor=styles.PHOTON_SPHERE_COLOR,
            linestyle=styles.PHOTON_SPHERE_LINESTYLE,
            linewidth=styles.PHOTON_SPHERE_LINEWIDTH,
            alpha=styles.PHOTON_SPHERE_ALPHA,
            zorder=5,
            label=r"Photon sphere $r=3M$"
        )

        self.ax.add_patch(
            self.photon_sphere
        )

    # ========================================================
    # ISCO
    # ========================================================

    def draw_isco(self):
        """
        Draw the innermost stable circular orbit.

        For Schwarzschild:

            r_ISCO = 6M
        """

        radius = 6.0 * self.M

        self.isco = Circle(
            (0.0, 0.0),
            radius,
            fill=False,
            edgecolor=styles.ISCO_COLOR,
            linestyle=styles.ISCO_LINESTYLE,
            linewidth=styles.ISCO_LINEWIDTH,
            alpha=styles.ISCO_ALPHA,
            zorder=4,
            label=r"ISCO $r=6M$"
        )

        self.ax.add_patch(
            self.isco
        )

    # ========================================================
    # Trajectory
    # ========================================================

    def draw_trajectory(
        self,
        r,
        phi,
        label="Geodesic",
        show_initial=True,
        show_final=True
    ):
        """
        Draw a geodesic trajectory.

        Parameters
        ----------
        r : ndarray
            Radial coordinate as a function of the integration
            parameter.

        phi : ndarray
            Azimuthal coordinate.

        label : str
            Legend label.

        show_initial : bool
            Show initial point.

        show_final : bool
            Show final point.

        Returns
        -------
        line
            Matplotlib Line2D object.
        """

        r = np.asarray(r)
        phi = np.asarray(phi)

        if r.shape != phi.shape:
            raise ValueError(
                "r and phi must have the same shape."
            )

        if r.size == 0:
            raise ValueError(
                "Trajectory cannot be empty."
            )

        x, y = spherical_to_cartesian(
            r,
            phi
        )

        line, = self.ax.plot(
            x,
            y,
            color=styles.TRAJECTORY_COLOR,
            linewidth=styles.TRAJECTORY_LINEWIDTH,
            alpha=styles.TRAJECTORY_ALPHA,
            label=label,
            zorder=3
        )

        if show_initial:

            self.ax.scatter(
                x[0],
                y[0],
                color=styles.INITIAL_POINT_COLOR,
                s=styles.INITIAL_POINT_SIZE,
                marker="o",
                zorder=20,
                label="Initial"
            )

        if show_final:

            self.ax.scatter(
                x[-1],
                y[-1],
                color=styles.FINAL_POINT_COLOR,
                s=styles.FINAL_POINT_SIZE,
                marker="x",
                zorder=20,
                label="Final"
            )

        return line

    # ========================================================
    # Multiple trajectories
    # ========================================================

    def draw_trajectories(
        self,
        trajectories,
        labels=None
    ):
        """
        Draw multiple geodesic trajectories.

        Parameters
        ----------
        trajectories : iterable
            Each trajectory must contain:

                trajectory.r
                trajectory.phi

        labels : iterable, optional
            Labels for trajectories.
        """

        if labels is None:
            labels = [
                f"Geodesic {i + 1}"
                for i in range(len(trajectories))
            ]

        for trajectory, label in zip(
            trajectories,
            labels
        ):

            self.draw_trajectory(
                trajectory.r,
                trajectory.phi,
                label=label,
                show_initial=False,
                show_final=False
            )

    # ========================================================
    # Reference circle
    # ========================================================

    def draw_reference_circle(
        self,
        radius,
        label=None,
        linestyle="--",
        linewidth=1.0,
        alpha=0.5
    ):
        """
        Draw an arbitrary circular reference surface.
        """

        x, y = circular_coordinates(
            radius
        )

        self.ax.plot(
            x,
            y,
            linestyle=linestyle,
            linewidth=linewidth,
            alpha=alpha,
            label=label
        )

    # ========================================================
    # Center
    # ========================================================

    def draw_center(self):
        """
        Draw the coordinate origin.
        """

        self.ax.scatter(
            0.0,
            0.0,
            s=10,
            color=styles.TEXT_COLOR,
            zorder=25
        )

    # ========================================================
    # Grid
    # ========================================================

    def draw_grid(self):
        """
        Draw the coordinate grid.
        """

        self.ax.grid(
            True,
            color=styles.GRID_COLOR,
            alpha=styles.GRID_ALPHA,
            linewidth=styles.GRID_LINEWIDTH
        )

    # ========================================================
    # Axes
    # ========================================================

    def draw_axes(self):
        """
        Configure coordinate axes.
        """

        self.ax.axhline(
            0.0,
            color=styles.AXIS_COLOR,
            alpha=styles.AXIS_ALPHA,
            linewidth=styles.AXIS_LINEWIDTH
        )

        self.ax.axvline(
            0.0,
            color=styles.AXIS_COLOR,
            alpha=styles.AXIS_ALPHA,
            linewidth=styles.AXIS_LINEWIDTH
        )

    # ========================================================
    # Labels
    # ========================================================

    def configure_labels(
        self,
        title="Schwarzschild Black Hole"
    ):
        """
        Configure title and axis labels.
        """

        self.ax.set_title(
            title,
            color=styles.TEXT_COLOR,
            fontsize=styles.TITLE_SIZE
        )

        self.ax.set_xlabel(
            r"$x/M$",
            color=styles.TEXT_COLOR,
            fontsize=styles.LABEL_SIZE
        )

        self.ax.set_ylabel(
            r"$y/M$",
            color=styles.TEXT_COLOR,
            fontsize=styles.LABEL_SIZE
        )

        self.ax.tick_params(
            colors=styles.TEXT_COLOR
        )

    # ========================================================
    # Aspect ratio
    # ========================================================

    def configure_aspect(self):
        """
        Keep the physical geometry undistorted.
        """

        self.ax.set_aspect(
            "equal",
            adjustable="box"
        )

    # ========================================================
    # Camera
    # ========================================================

    def apply_camera(self):
        """
        Apply camera limits.
        """

        self.camera.apply(
            self.ax
        )

    # ========================================================
    # Legend
    # ========================================================

    def draw_legend(self):
        """
        Draw the legend if there are labeled objects.
        """

        handles, labels = self.ax.get_legend_handles_labels()

        if not labels:
            return

        legend = self.ax.legend()

        legend.get_frame().set_facecolor(
            "black"
        )

        legend.get_frame().set_alpha(
            0.8
        )

        for text in legend.get_texts():

            text.set_color(
                styles.TEXT_COLOR
            )

    # ========================================================
    # Complete scene
    # ========================================================

    def draw_scene(
        self,
        draw_horizon=True,
        draw_photon_sphere=True,
        draw_isco=True,
        draw_grid=True,
        draw_axes=True,
        draw_center=True,
        title="Schwarzschild Black Hole"
    ):
        """
        Draw the complete static black-hole scene.

        This does not draw trajectories.
        """

        if draw_grid:
            self.draw_grid()

        if draw_axes:
            self.draw_axes()

        if draw_isco:
            self.draw_isco()

        if draw_photon_sphere:
            self.draw_photon_sphere()

        if draw_horizon:
            self.draw_black_hole()

        if draw_center:
            self.draw_center()

        self.configure_aspect()

        self.configure_labels(
            title=title
        )

        self.apply_camera()

    # ========================================================
    # Automatic camera
    # ========================================================

    def fit_to_trajectory(
        self,
        r,
        phi,
        margin=styles.DEFAULT_MARGIN
    ):
        """
        Automatically fit camera to a trajectory.
        """

        x, y = spherical_to_cartesian(
            r,
            phi
        )

        self.camera.fit_to_data(
            x,
            y,
            margin=margin
        )

        self.apply_camera()

    # ========================================================
    # Show
    # ========================================================

    def show(self):
        """
        Display the rendered scene.
        """

        self.draw_legend()

        plt.show()

    # ========================================================
    # Save
    # ========================================================

    def save(
        self,
        filename,
        dpi=300,
        transparent=False
    ):
        """
        Save rendered image.
        """

        self.fig.savefig(
            filename,
            dpi=dpi,
            transparent=transparent,
            bbox_inches="tight"
        )

    # ========================================================
    # Close
    # ========================================================

    def close(self):
        """
        Close Matplotlib figure.
        """

        plt.close(
            self.fig
        )