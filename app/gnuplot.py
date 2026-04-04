"""Gnuplot wrapper — generate publication-quality plots via gnuplot.

All GNA instruments use this module instead of matplotlib for
final output plots. Gnuplot scripts are generated as temp files,
executed, and the resulting image is loaded into a QPixmap.
"""

import subprocess
import tempfile
from pathlib import Path
from typing import Optional

from PyQt6.QtGui import QPixmap


# ── Gnuplot style matching the IFIN-HH proposal figure ──
# White background, black axes, log-Y where needed, clean serif-ish font.
_PREAMBLE = """\
set encoding utf8
set terminal pngcairo enhanced font "Helvetica,14" size {width},{height}
set output '{output}'
set style line 100 lc rgb "#888888" lt 1 lw 0.5
set grid ls 100
set border lw 1.5
set tics out nomirror
set key right top font "Helvetica,12" spacing 1.2 box
"""

# Colour cycle for data series (matches proposal figure palette)
SERIES_COLORS = [
    "#e41a1c",  # red
    "#377eb8",  # blue
    "#4daf4a",  # green
    "#ff7f00",  # orange
    "#984ea3",  # purple
    "#00bcd4",  # cyan
    "#a65628",  # brown
    "#f781bf",  # pink
    "#999999",  # grey
    "#e6ab02",  # gold
]

SERIES_MARKERS = [
    5, 7, 9, 11, 13,   # pointtype: square, circle, triangle, diamond, invtri
    4, 6, 8, 10, 12,   # filled variants
]


def _write_data_block(f, columns: list[list[float]]) -> None:
    """Write a gnuplot inline data block (rows from zipped columns)."""
    for row in zip(*columns):
        f.write(" ".join(f"{v:.6g}" for v in row) + "\n")
    f.write("e\n")


def run_script(script: str) -> str:
    """Execute a gnuplot script string. Returns gnuplot's stderr output."""
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".gp", delete=False
    ) as f:
        f.write(script)
        f.flush()
        result = subprocess.run(
            ["gnuplot", f.name],
            capture_output=True, text=True, timeout=30,
        )
    if result.returncode != 0:
        raise RuntimeError(f"gnuplot error:\n{result.stderr}")
    return result.stderr


def plot_xy(
    series: list[dict],
    *,
    title: str = "",
    xlabel: str = "x",
    ylabel: str = "y",
    logx: bool = False,
    logy: bool = False,
    width: int = 900,
    height: int = 600,
    output: Optional[str] = None,
    extra_commands: str = "",
) -> tuple[str, QPixmap]:
    """Plot one or more x-y series with gnuplot.

    Parameters
    ----------
    series : list of dict
        Each dict has:
            'x' : list[float]
            'y' : list[float]
            'label' : str
            'with' : str  (optional, default "linespoints")
            'xerr' : list[float]  (optional)
            'yerr' : list[float]  (optional)
    title, xlabel, ylabel : str
    logx, logy : bool
    width, height : int  (pixels)
    output : str or None
        If None, a temp PNG is created.
    extra_commands : str
        Extra gnuplot commands injected after the preamble.

    Returns
    -------
    (path, pixmap) : tuple
        Path to the PNG file and a QPixmap loaded from it.
    """
    if output is None:
        tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        output = tmp.name
        tmp.close()

    lines = [_PREAMBLE.format(width=width, height=height, output=output)]

    if title:
        lines.append(f"set title '{_esc(title)}' font 'Helvetica,16'")
    lines.append(f"set xlabel '{_esc(xlabel)}'")
    lines.append(f"set ylabel '{_esc(ylabel)}'")

    if logx:
        lines.append("set logscale x")
    if logy:
        lines.append("set logscale y")
        lines.append("set format y '10^{%T}'")

    if extra_commands:
        lines.append(extra_commands)

    # Build plot command
    plot_parts = []
    for idx, s in enumerate(series):
        color = SERIES_COLORS[idx % len(SERIES_COLORS)]
        pt = SERIES_MARKERS[idx % len(SERIES_MARKERS)]
        style = s.get("with", "linespoints")
        label = _esc(s.get("label", f"series {idx+1}"))
        has_xerr = "xerr" in s and s["xerr"]
        has_yerr = "yerr" in s and s["yerr"]

        if has_xerr and has_yerr:
            using = "1:2:3:4"
            style = "xyerrorbars"
        elif has_yerr:
            using = "1:2:3"
            style = "yerrorbars"
        elif has_xerr:
            using = "1:2:3"
            style = "xerrorbars"
        else:
            using = "1:2"

        ls_def = (
            f"set style line {idx+1} lc rgb '{color}' lt 1 lw 2 "
            f"pt {pt} ps 1.5"
        )
        lines.append(ls_def)
        plot_parts.append(
            f"'-' using {using} with {style} ls {idx+1} title '{label}'"
        )

    lines.append("plot " + ", \\\n     ".join(plot_parts))

    # Inline data blocks
    for s in series:
        has_xerr = "xerr" in s and s["xerr"]
        has_yerr = "yerr" in s and s["yerr"]
        cols = [s["x"], s["y"]]
        if has_xerr and has_yerr:
            cols.extend([s["xerr"], s["yerr"]])
        elif has_yerr:
            cols.append(s["yerr"])
        elif has_xerr:
            cols.append(s["xerr"])

        for row in zip(*cols):
            lines.append(" ".join(f"{v:.6g}" for v in row))
        lines.append("e")

    script = "\n".join(lines) + "\n"
    run_script(script)

    pixmap = QPixmap(output)
    return output, pixmap


def plot_rdds(
    x: list[float],
    x_err: list[float],
    y: list[float],
    y_err: list[float],
    fit_x: list[float],
    fit_y: list[float],
    t_half_label: str,
    *,
    output: Optional[str] = None,
    width: int = 900,
    height: int = 600,
) -> tuple[str, QPixmap]:
    """Plot RDDS decay curve: data with error bars + ODR fit line.

    Returns (path, pixmap).
    """
    if output is None:
        tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        output = tmp.name
        tmp.close()

    script = _PREAMBLE.format(width=width, height=height, output=output)
    script += f"""
set title 'Linear Fit to Determine Half-Life' font 'Helvetica,16'
set xlabel 'Plunger distance (μm)'
set ylabel 'ln(I_u / (I_u + I_s))'
set xrange [0:*]
set label 1 'T_{{1/2}} {_esc(t_half_label)}' at graph 0.05, graph 0.92 \\
    font 'Helvetica,18' tc rgb '#000000'
set style line 1 lc rgb '#e41a1c' lt 1 lw 2 pt 7 ps 1.8
set style line 2 lc rgb '#377eb8' lt 1 lw 2.5
plot '-' using 1:2:3:4 with xyerrorbars ls 1 title 'Data', \\
     '-' using 1:2 with lines ls 2 title 'ODR fit'
"""
    # Data block
    for xi, yi, xei, yei in zip(x, y, x_err, y_err):
        script += f"{xi:.6g} {yi:.6g} {xei:.6g} {yei:.6g}\n"
    script += "e\n"
    # Fit line block
    for xi, yi in zip(fit_x, fit_y):
        script += f"{xi:.6g} {yi:.6g}\n"
    script += "e\n"

    run_script(script)
    pixmap = QPixmap(output)
    return output, pixmap


def plot_pace4(
    channels: dict[str, dict[float, float]],
    reaction_label: str = "",
    *,
    output: Optional[str] = None,
    width: int = 900,
    height: int = 600,
) -> tuple[str, QPixmap]:
    """Plot PACE4 σ(E) for selected residue channels.

    Parameters
    ----------
    channels : dict
        label → {energy_MeV: xsec_mb}
    reaction_label : str
        e.g. "^{11}B + ^{100}Mo"

    Returns (path, pixmap).
    """
    if output is None:
        tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        output = tmp.name
        tmp.close()

    title = reaction_label if reaction_label else "PACE4 Reaction Cross Sections"

    script = _PREAMBLE.format(width=width, height=height, output=output)
    script += f"""
set title '{_esc(title)}' font 'Helvetica,16'
set xlabel 'E [MeV]'
set ylabel 'CS [mb]'
set logscale y
set format y '10^{{%T}}'
set yrange [0.5:*]
"""

    sorted_channels = sorted(
        channels.items(),
        key=lambda kv: max(kv[1].values()),
        reverse=True,
    )

    plot_parts = []
    for idx, (label, _) in enumerate(sorted_channels):
        color = SERIES_COLORS[idx % len(SERIES_COLORS)]
        pt = SERIES_MARKERS[idx % len(SERIES_MARKERS)]
        script += (
            f"set style line {idx+1} lc rgb '{color}' lt 1 lw 2 "
            f"pt {pt} ps 1.8\n"
        )
        gp_label = _nuclide_to_gnuplot(label)
        plot_parts.append(
            f"'-' using 1:2 with linespoints ls {idx+1} title '{gp_label}'"
        )

    script += "plot " + ", \\\n     ".join(plot_parts) + "\n"

    for _, pts in sorted_channels:
        for e in sorted(pts.keys()):
            script += f"{e:.6g} {pts[e]:.6g}\n"
        script += "e\n"

    run_script(script)
    pixmap = QPixmap(output)
    return output, pixmap


def _nuclide_to_gnuplot(label: str) -> str:
    """Convert '107Ag' → '^{107}Ag' for gnuplot enhanced text."""
    i = 0
    while i < len(label) and label[i].isdigit():
        i += 1
    if i > 0:
        return "^{" + label[:i] + "}" + label[i:]
    return label


def _esc(text: str) -> str:
    """Escape single quotes for gnuplot strings."""
    return text.replace("'", "''")
