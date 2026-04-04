"""Talmi Empirical Shell Model B(E2) calculator.

Physical basis
--------------
The Talmi procedure computes B(E2) transition probabilities for nuclei
in the g_{9/2} (j = 9/2) shell by:

1. Taking an input vector of empirical reduced matrix elements squared
   (or theoretical effective charges / B(E2; 2+ -> 0+) systematics).
2. Applying sqrt() to obtain reduced matrix elements.
3. Multiplying by a fixed 14×4 weighting-factor matrix whose entries
   come from shell-model Clebsch-Gordan and Racah algebra for j=9/2.
   (See I. Talmi, "Simple Models of Complex Nuclei", Table IV.)
4. Squaring the resulting vector to obtain B(E2) values in Weisskopf units.

The 14 output rows correspond to the allowed
    J_i -> J_f  E2 transitions within the g_{9/2} multiplet.
"""

import math
import json
from pathlib import Path


DEFAULT_WEIGHTS_PATH = Path(__file__).parent.parent.parent.parent / (
    "data" / Path("weighting_factors.json")
)
# Fallback: try the ESMcalc repo location
ESMC_WEIGHTS_PATH = Path.home() / "repos" / "ESMcalc" / "weighting_factors.json"

TRANSITION_LABELS = [
    ("3/2", "5/2"),
    ("3/2", "7/2"),
    ("5/2", "7/2"),
    ("5/2", "9/2"),
    ("7/2", "9/2"),
    ("11/2", "7/2"),
    ("11/2", "9/2"),
    ("11/2", "13/2"),
    ("13/2", "9/2"),
    ("15/2", "11/2"),
    ("15/2", "13/2"),
    ("17/2", "13/2"),
    ("17/2", "15/2"),
    ("21/2", "17/2"),
]


def load_weighting_matrix(path=None):
    """Load and evaluate the 14×4 Talmi weighting factor matrix.

    The JSON entries may be numbers or string math expressions like
    ``"307/121*math.sqrt(2/35)"`` — these are evaluated safely.
    """
    if path is None:
        if DEFAULT_WEIGHTS_PATH.exists():
            path = DEFAULT_WEIGHTS_PATH
        elif ESMC_WEIGHTS_PATH.exists():
            path = ESMC_WEIGHTS_PATH
        else:
            raise FileNotFoundError(
                "weighting_factors.json not found.\n"
                f"Tried: {DEFAULT_WEIGHTS_PATH}\n"
                f"   and {ESMC_WEIGHTS_PATH}"
            )

    with open(path) as f:
        raw_matrix = json.load(f)

    safe_globals = {"__builtins__": {}, "math": math}
    evaluated = []
    for row in raw_matrix:
        eval_row = []
        for item in row:
            if isinstance(item, (int, float)):
                eval_row.append(float(item))
            elif isinstance(item, str):
                val = eval(item, safe_globals, {})  # noqa: S307
                eval_row.append(float(val))
            else:
                raise ValueError(f"Unsupported coefficient: {item!r}")
        evaluated.append(eval_row)
    return evaluated


def compute_be2(input_vector, weighting_matrix):
    """Compute B(E2) transition probabilities via the Talmi procedure.

    Parameters
    ----------
    input_vector : list of float
        4 values — empirical B(E2) data or effective-charge matrix elements.
    weighting_matrix : list[list[float]]
        14×4 evaluated weighting-factor matrix.

    Returns
    -------
    list of float
        14 B(E2) values in Weisskopf units (W.u.).
    """
    sqrt_vec = [math.sqrt(x) if x >= 0 else float("nan") for x in input_vector]

    n_cols = len(weighting_matrix[0])
    if n_cols != len(sqrt_vec):
        raise ValueError(
            f"Input vector length {len(sqrt_vec)} does not match "
            f"matrix column count {n_cols}"
        )

    results = []
    for row in weighting_matrix:
        dot = sum(c * v for c, v in zip(row, sqrt_vec))
        results.append(round(dot ** 2, 2))
    return results


def parse_input_json(path):
    """Parse an ESMcalc input JSON file (supports legacy and multi-dataset formats).

    Returns
    -------
    source_nucleus, target_nucleus : str or None
    datasets : list of dict
        Each with keys 'method' and 'vector'.
    """
    with open(path) as f:
        data = json.load(f)

    if isinstance(data, list):
        if len(data) == 1 and isinstance(data[0], list):
            return None, None, [{"method": "Default", "vector": data[0]}]
        return None, None, [{"method": "Default", "vector": data}]

    if isinstance(data, dict):
        source = data.get("source_nucleus")
        target = data.get("target_nucleus")

        if "datasets" in data:
            datasets = []
            for ds in data["datasets"]:
                vec = ds.get("vector") or ds.get("input")
                method = ds.get("method", "Default")
                datasets.append({"method": method, "vector": vec})
            return source, target, datasets

        if "vector" in data or "input" in data:
            vec = data.get("vector") or data.get("input")
            return source, target, [{"method": "Default", "vector": vec}]

    raise ValueError("Unsupported input JSON format")
