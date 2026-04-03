"""Matplotlib integration for RDDS plots (embedded in PyQt6)."""

import numpy as np
import matplotlib
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from app.theme import PLOT_STYLE


def create_canvas(figsize=(7, 4.5)):
    """Create a matplotlib Figure + FigureCanvas styled for GNA."""
    matplotlib.rcParams.update(PLOT_STYLE)
    fig = Figure(figsize=figsize, tight_layout=True)
    canvas = FigureCanvasQTAgg(fig)
    return fig, canvas


def plot_rdds_fit(fig, x, x_err, y, y_err, odr_result, t_half_label):
    """Plot RDDS ln(R) vs distance data with the ODR linear fit.

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        The figure to draw on (will be cleared first).
    x, x_err : array-like
        Distance values and uncertainties (micro-meters).
    y, y_err : array-like
        ln(R) values and uncertainties.
    odr_result : scipy.odr.Output
        ODR regression result (slope = beta[0], intercept = beta[1]).
    t_half_label : str
        Formatted half-life string to display on the plot.
    """
    fig.clear()
    matplotlib.rcParams.update(PLOT_STYLE)
    ax = fig.add_subplot(111)

    # Data with error bars
    ax.errorbar(
        x, y, xerr=x_err, yerr=y_err,
        fmt='none', capsize=8, color='#f7768e', alpha=0.7, linewidth=1.5,
    )
    ax.scatter(x, y, color='#f7768e', s=60, zorder=5, label='Data')

    # Fit line
    margin = (max(x) - min(x)) * 0.08
    x_fit = np.linspace(min(x) - margin, max(x) + margin, 500)
    y_fit = odr_result.beta[0] * x_fit + odr_result.beta[1]
    ax.plot(x_fit, y_fit, color='#7aa2f7', linewidth=2, label='ODR fit')

    ax.set_xlabel(r"Plunger distance ($\mu$m)")
    ax.set_ylabel(r"$\ln\!\left(\frac{I_u}{I_u + I_s}\right)$")
    ax.set_title("RDDS — Decay Curve Fit", pad=12)

    ax.text(
        0.05, 0.95, f"$T_{{1/2}}$ {t_half_label}",
        transform=ax.transAxes, verticalalignment='top', fontsize=12,
        color='#9ece6a',
        bbox=dict(
            boxstyle='round,pad=0.4', facecolor='#1e1e2e',
            edgecolor='#3b4261', alpha=0.9,
        ),
    )

    ax.legend(loc='lower left', framealpha=0.8)
    ax.grid(True, linestyle='--', linewidth=0.5)
    fig.tight_layout()
