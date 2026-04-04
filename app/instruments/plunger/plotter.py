"""Gnuplot-based RDDS plotting (replaces matplotlib version)."""

import numpy as np
from app import gnuplot


def plot_rdds_fit(x, x_err, y, y_err, odr_result, t_half_label):
    """Plot RDDS ln(R) vs distance with ODR fit using gnuplot.

    Returns (image_path, QPixmap).
    """
    # Build fit line — clamp to non-negative distances
    margin = (max(x) - min(x)) * 0.08
    x_lo = max(0, min(x) - margin)
    x_fit = np.linspace(x_lo, max(x) + margin, 200)
    y_fit = odr_result.beta[0] * x_fit + odr_result.beta[1]

    return gnuplot.plot_rdds(
        x=list(x),
        x_err=list(x_err),
        y=list(y),
        y_err=list(y_err),
        fit_x=list(x_fit),
        fit_y=list(y_fit),
        t_half_label=t_half_label,
    )
