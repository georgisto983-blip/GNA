# GNA — Georgi's Nuclear Assistant

**A desktop application for experimental nuclear structure physics.**

GNA is a toolbox built for nuclear physicists working in γ-ray spectroscopy and
nuclear structure.  It brings together the most common calculations you need
during an experiment — half-life extraction from RDDS data, beam kinematics,
angular-momentum coupling, cross-section analysis, and shell-model estimates —
into a single, themed desktop app with publication-quality plotting.

| | |
|---|---|
| **Author** | Georgi Stoev |
| **Version** | 2.0 |
| **License** | MIT |
| **Stack** | Python 3.12 · PyQt6 · gnuplot · scipy · numpy |

---

## Table of Contents

1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [The Six Tools](#the-six-tools)
   - [Plunger (RDDS)](#1-plunger-rdds)
   - [J-Coupling](#2-j-coupling)
   - [Talmi Calculator](#3-talmi-calculator)
   - [PACE4](#4-pace4)
   - [Script Launcher](#5-script-launcher)
   - [Accelerator](#6-accelerator)
4. [JSON File Reference](#json-file-reference)
5. [Creating Your Own Input Files](#creating-your-own-input-files)
6. [Themes](#themes)
7. [Desktop Shortcut](#desktop-shortcut)
8. [Troubleshooting](#troubleshooting)
9. [Roadmap](#roadmap)

---

## Installation

### Requirements

- **Python 3.10+** (tested on 3.12)
- **gnuplot 5.4+** (for all plots)
- **Linux** (tested on Ubuntu; may work on other distros)

### Steps

```bash
# 1.  Clone or download the repository
git clone https://github.com/georgisto983-blip/GNA.git
cd GNA

# 2.  Create a virtual environment and install dependencies
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 3.  Make sure gnuplot is installed
sudo apt install gnuplot        # Debian / Ubuntu
# or: sudo dnf install gnuplot  # Fedora

# 4.  Run
python3 main.py
# or simply:
./run.sh
```

> **Tip:** `run.sh` activates the venv and launches the app in one step.

---

## Quick Start

1. Launch GNA.  You will see a **welcome screen** with the app logo.
2. Pick a tool from the **sidebar** on the left (e.g. *Plunger (RDDS)*).
3. Enter your data manually **or** load a JSON file with the *Load from JSON*
   button / tab.
4. Click **Calculate** (or **Plot**).
5. Results appear in the panel; most tools also offer a pop-out **Result
   Window** with **PDF export**.

Every tool ships with example JSON files in the `example_data/` folder so you
can try things out immediately.

---

## The Six Tools

### 1. Plunger (RDDS)

Extracts nuclear excited-state **half-lives** using the Recoil Distance Doppler
Shift (RDDS) method — the standard technique in γ-ray spectroscopy for
measuring lifetimes of nuclear states in the range of ~0.5–500 ps.

#### How it works

A thin target foil and a stopper (or degrader) foil are separated by a
precisely controlled distance *d*.  Nuclei recoil out of the target at
velocity *βc* and de-excite in flight.  The γ-ray spectrum contains two peaks
for each transition: a **Doppler-shifted** peak (decay in flight) and an
**unshifted** peak (decay after the stopper).  The ratio of these peaks, as a
function of *d*, gives the lifetime.

GNA implements two modes:

| Mode | Tab | What it does |
|---|---|---|
| **Single distance** | *Single Distance* | Given one (d, β, A_s, A_u) data point, calculates T₁/₂ directly from the exponential decay law |
| **Multiple distances** | *Multiple Distances* | Given an array of distances with peak areas, performs a weighted linear fit (ODR — orthogonal distance regression, so both x and y uncertainties are used) to ln(A_u / A_s) vs. d and extracts T₁/₂ from the slope |

#### Inputs

| Field | Meaning | Units | Example |
|---|---|---|---|
| Distance *d* | Target–stopper gap | µm | 13 ± 0.5 |
| β | Recoil velocity *v/c* | dimensionless | 0.008 ± 0.0001 |
| Area shifted | Doppler-shifted peak area | counts | 7601 ± 300 |
| Area unshifted | Unshifted peak area | counts | 4300 ± 90 |

Every value is entered as `value uncertainty` (e.g. `13 0.5`).

#### Output

- **T₁/₂** in picoseconds, with propagated uncertainty
- **Gnuplot fit plot** (multi-distance mode): linear fit on a ln(R) vs *d*
  graph, with the half-life printed on the plot
- Result window with PDF export

#### Try it

Load `example_data/plunger_single.json` or `example_data/plunger_multi.json`.

---

### 2. J-Coupling

Calculates **angular momentum coupling** for identical nucleons in a single-*j*
shell.  If you have *n* nucleons in an orbital with angular momentum *j*, this
tool enumerates all allowed total spin values *J* using the *m*-scheme.

#### What it solves

In the nuclear shell model, when you place several nucleons in the same orbital
(say, the g₉/₂ shell), only certain total angular momenta *J* are allowed by
the Pauli exclusion principle.  This tool lists them and shows the number of
*m_j* sub-state combinations that make up each *J* state.

#### Inputs

| Field | Meaning | Example |
|---|---|---|
| Z | Proton number | 47 |
| N | Neutron number | 60 |
| j orbital | Single-particle angular momentum | 9/2 |
| n particles | Number of nucleons in the shell | 3 |

You can also enter Z and N and let the tool suggest the active shell and
occupancy from the standard shell-model filling order.

#### Output

- Table of allowed *J* values
- Number of *m_j* combinations per *J*
- Shell occupancy analysis (which shells are filled, which is active)

#### Try it

Load `example_data/j_coupling.json`.

---

### 3. Talmi Calculator

Computes **B(E2) transition probabilities** for the g₉/₂ shell using the
**Talmi empirical shell model** procedure.

#### Background

B(E2) values describe how strongly a nucleus emits E2 (electric quadrupole)
γ-rays during a transition.  They directly reflect the nuclear shape:
large B(E2) → very collective (deformed) nucleus.  The Talmi procedure for
the *j* = 9/2 multiplet uses a 14×4 weighting matrix (stored in
`data/weighting_factors.json`) that contains Clebsch–Gordan algebra built
into the g₉/₂ shell model.

You supply **4 empirical input values** (from experiment or theory) per dataset
method.  The calculator multiplies them through the weighting matrix to produce
all **14 B(E2)** values for transitions within the multiplet, in Weisskopf units
(W.u.).

#### Inputs

**Manual mode** — enter values in a table:

| Column | Meaning |
|---|---|
| Method Name | Label for this dataset (e.g. "Experimental", "SM calc") |
| v₁ … v₄ | Four empirical B(E2) input values |

You can add multiple datasets (rows) and compare them side by side.

**JSON mode** — load a file like `example_data/talmi_calculator.json`.

#### Output

- Table of 14 transitions with B(E2) values for each dataset
- Pop-out result window with PDF export
- You can also import a custom weighting matrix if needed

---

### 4. PACE4

Analyses **PACE4** statistical-model output files to plot **residue
cross-sections σ(E)** as a function of beam energy.

#### What is PACE4?

PACE4 is a statistical evaporation code (available inside
[LISE++](http://lise.nscl.msu.edu/lise.html)) that predicts which nuclei are
produced when a beam hits a target.  It outputs HTML files containing tables of
residue nuclei and their production cross-sections at a given beam energy.

#### Workflow

1. **Generate** PACE4 HTML files from LISE++ — one file per beam energy step
2. **Load** them into GNA (Add File(s) button — accepts any file, no extension
   restriction)
3. GNA parses each file, extracts the beam energy and all residue cross-sections
4. **Residue Table** tab: inspect individual files, see yields and percentages
5. **CS vs Energy** tab: select residue channels from the ranked list, click
   *Plot with gnuplot*

#### Legend placement

The **Legend** dropdown lets you choose where the legend appears on the plot:

| Style | Behaviour |
|---|---|
| Top-right (default) | Inside the plot, top-right corner |
| Outside right | Legend outside the plot area — never overlaps data |
| Top-right opaque | Same corner, but with a solid background so lines can't bleed through |

#### Output

- Publication-quality gnuplot plot: log-Y scale, coloured markers + lines,
  superscript mass numbers (e.g. ¹⁰⁷Ag)
- Save as PNG, SVG, or PDF
- Result window for the residue table

#### Try it

Load the files in `example_data/PACE4_test/` (21 energy steps for ¹³C + ¹⁰⁰Mo).

---

### 5. Script Launcher

A **shell-script runner** for automating repetitive tasks during data sorting —
especially matrix-cutting and autosort operations common in multi-detector
γ-ray experiments.

#### What it does

- Lets you **configure a working directory** (saved in `config/settings.json`)
- Lists shell scripts (`.sh`) from that directory
- **Run** any script with one click; live stdout/stderr appears in the
  embedded terminal output
- **Matrix operations** buttons: run bulk cutting/autosort scripts across all
  distance subdirectories in your data

This is most useful during offline sorting of multi-detector data, where you
need to run the same scripts across dozens of distance directories.

#### Configuration

Edit `config/settings.json` or use the UI to set your script directory:

```json
{
  "script_directories": [
    "/path/to/your/matrices"
  ]
}
```

#### Try it

Point it to `example_data/script_launcher_test/matrices/` to see example
scripts and directory structure.

---

### 6. Accelerator

A two-in-one tool for **beam kinematics** and **beam-on-target yield
estimates**.

#### Kinematics tab

Given a beam and target, calculates:

| Output | Formula / Notes |
|---|---|
| Beam velocity β | From relativistic kinematics: E = (γ−1)·A·u |
| Beam velocity v | β × c [µm/ps, useful for RDDS] |
| Coulomb barrier V_C | With r₀ = 1.35 fm |
| CN recoil β and v | Two-body momentum conservation |
| Nuclear radii | R = r₀ · A^(1/3), r₀ = 1.2 fm |

#### Beam Yield tab

Estimates the **expected γ-ray count rate** from a beam-on-target experiment:

| Input | Meaning | Example |
|---|---|---|
| Beam current | In particle-nA (pnA) | 2 |
| Cross-section | Production cross-section (mb) | 70 |
| Target thickness | mg/cm² | 1.3 |
| Target A | Mass number of the target | 100 |
| Detector efficiency | Fraction (0–1) | 0.01 |
| Excitation ratio | Fraction of nuclei produced in the state of interest | 0.08 |
| Sorter efficiency | Data-acquisition live-time fraction | 0.05 |

Output: counts/s, counts/hour, counts per 8-hour shift.

#### Try it

Load `example_data/kinematics.json` or `example_data/beam_yield.json`.

---

## JSON File Reference

All GNA tools can load and save data as JSON.  Here are the schemas:

### Plunger — single distance

```json
{
    "plunger_distance": "13 0.5",
    "beta": "0.008 0.0001",
    "area_shifted": "7601 300",
    "area_unshifted": "4300 90"
}
```

Each value is a string: `"value uncertainty"`.

### Plunger — multiple distances

```json
{
    "beta": [0.008, 0.0001],
    "plunger_distance": [
        [11, 0.5],
        [13, 0.5]
    ],
    "area_shifted": [
        [2510, 55],
        [2997, 60]
    ],
    "area_unshifted": [
        [9530, 107],
        [9146, 105]
    ]
}
```

Arrays of `[value, uncertainty]` pairs.  The `beta` array is a single pair
(same recoil velocity for all distances).

### Kinematics

```json
{
    "beam_energy_MeV": 59,
    "beam_A": 13,
    "beam_Z": 6,
    "target_A": 100,
    "target_Z": 42
}
```

### Beam Yield

```json
{
    "beam_current_pnA": 2,
    "cross_section_mb": 70,
    "target_thickness_mg_cm2": 1.3,
    "target_A": 100,
    "detector_efficiency": 0.01,
    "excitation_ratio": 0.08,
    "sorter_efficiency": 0.05
}
```

### J-Coupling

```json
{
    "Z": 47,
    "N": 60,
    "nucleus_name": "107Ag",
    "j_orbital": "9/2",
    "n_particles": 3
}
```

### Talmi Calculator

```json
{
    "source_nucleus": "104Cd",
    "target_nucleus": "103Ag",
    "datasets": [
        {
            "method": "Experimental",
            "vector": [11.5, 8.2, 21.0, 5.8]
        }
    ]
}
```

You can add multiple objects to the `datasets` array to compare different
methods (e.g. experimental vs. shell-model values).

---

## Creating Your Own Input Files

### General rules

1. **Use any text editor** (VS Code, nano, gedit, etc.)
2. Files must be **valid JSON** — keys in double quotes, no trailing commas
3. Copy an example file from `example_data/` and change the numbers
4. GNA's file dialogs always offer *All Files (\*)* so you can use any
   extension (`.json`, `.dat`, `.txt`, etc.)

### PACE4 HTML files

These are generated by **LISE++ → PACE4**, not written by hand.  Each file
corresponds to one beam energy.  To use them in GNA:

1. In LISE++, run PACE4 for your reaction at multiple energies
2. Save each result as an HTML file (the file names don't matter)
3. In GNA → PACE4 → Add Files, select all of them at once
4. GNA will parse the beam energy and residue table from each file automatically

### Script Launcher scripts

These are ordinary Bash scripts.  Place them in a directory and point GNA's
Script Launcher to that directory.  Example structure:

```
matrices/
├── Cut_Fw_Fw.sh          # main cutting script
├── Cut_Fw_Bw.sh
├── matrices_Autosort_all.sh
├── 11um/                  # one subdirectory per plunger distance
│   ├── Autosort
│   ├── 0proje.setup
│   └── *.cmat
├── 13um/
└── 16um/
```

### Weighting factors matrix

The file `data/weighting_factors.json` contains the 14×4 Talmi weighting matrix
for the g₉/₂ shell.  Each entry is either `0` or a string containing a Python
math expression (e.g. `"307/121*math.sqrt(2/35)"`).  GNA evaluates these at
runtime.  You should not need to change this file unless you are working with a
different j-shell and have derived your own matrix.

---

## Themes

GNA ships with **8 colour themes** — 4 dark and 4 light:

| Dark | Light |
|---|---|
| Neon Prism *(default)* | Neon Prism Light |
| Ultraviolet | Ultraviolet Light |
| Plasma Burst | Plasma Burst Light |
| Celestial | Celestial Light |

Switch themes at any time using the **Theme** dropdown at the bottom of the
sidebar.  The theme applies to the entire UI and to embedded matplotlib plots.

---

## Desktop Shortcut

To create a clickable icon on your Linux desktop:

```bash
# 1.  Make it executable
chmod +x gna.desktop

# 2.  Copy to desktop
cp gna.desktop ~/Desktop/

# 3.  (GNOME) Trust it so it becomes clickable
gio set ~/Desktop/gna.desktop metadata::trusted true
```

The `.desktop` file references the SVG icon in `assets/gna-icon.svg` and
launches via `run.sh`.  If you move the GNA folder, update the paths in
`gna.desktop`.

Optionally, install it to your application menu:

```bash
cp gna.desktop ~/.local/share/applications/
```

---

## Troubleshooting

| Problem | Solution |
|---|---|
| `gnuplot: command not found` | Install gnuplot: `sudo apt install gnuplot` |
| `ModuleNotFoundError: PyQt6` | Activate the venv: `source .venv/bin/activate` |
| PACE4 file not loading | Make sure it is an actual PACE4 HTML output (not the LISE++ GUI page). Use *All Files* in the dialog |
| Plot looks blank / tiny | Check that gnuplot is version 5.4+ (`gnuplot --version`) |
| Theme combo is empty | Verify `app/theme.py` is not corrupted; re-pull from git |
| Script Launcher shows no scripts | Set the script directory in the UI or edit `config/settings.json` |

---

## Roadmap

Planned features for future versions:

- **Experiment report** — export all results from a session to a single PDF

### Implemented in v2.0

- **In-app Help panel** — click *Help* in the sidebar to view the full
  documentation rendered inside the app, with section navigation
- **Status bar** with quick-reference physics constants (c, r₀, u, Nₐ, ℏ)
  visible at all times along the bottom
- **Recent files** — the welcome screen shows your last-loaded files so you
  can quickly see what you worked on; tracked automatically when you load
  JSON or PACE4 files
- **Undo / redo** — all text input fields support Ctrl+Z (undo) and
  Ctrl+Shift+Z (redo) natively
- **8 colour themes** with runtime switching (4 dark + 4 light)

---

*GNA is free and open-source software under the MIT License.*
