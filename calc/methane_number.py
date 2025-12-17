"""
Methane number estimation (simplified AVL-style TMN method).

This implementation follows a grouped-component / TMN table approach
inspired by EN 16726:2015 Annex A, but it is NOT a full implementation
of the official AVL ternary-mixture method. :contentReference[oaicite:1]{index=1}
"""

from __future__ import annotations

from typing import Dict
import warnings

# --- Component groups ---------------------------------------------------------

# Group definitions (A/B/C) broadly aligned with EN 16726 families
GROUP_A = frozenset({"CH4", "C2H6"})
GROUP_B = frozenset({"C3H8", "iC4H10", "nC4H10"})
# Group C includes the heavier and inert components
GROUP_C_COMPONENTS = frozenset(
    {
        "iC5H12",
        "nC5H12",
        "C6H14",
        "C7plus",
        "N2",
        "CO2",
        "H2S",
        "H2O",
    }
)

ALLOWED_COMPONENTS = GROUP_A | GROUP_B | GROUP_C_COMPONENTS

# Number of carbon atoms per component
# C7plus approximated as 7 carbon atoms
CARBON_ATOMS: Dict[str, int] = {
    "CH4": 1,
    "C2H6": 2,
    "C3H8": 3,
    "iC4H10": 4,
    "nC4H10": 4,
    "iC5H12": 5,
    "nC5H12": 5,
    "C6H14": 6,
    "C7plus": 7,
    # “Inert” components – carbon count only matters for CO2 here
    "N2": 0,
    "CO2": 1,
    "H2S": 0,
    "H2O": 0,
}

# --- TMN table and Mnemo grids -----------------------------------------------

# TMN table at intersections of Mnemo_B (rows) and Mnemo_C (columns)
# Mnemo_B: [1.0, 2.0, 3.0, 4.0]
# Mnemo_C: [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
TMN_TABLE = [
    # Row for Mnemo_B = 1.0
    [100.0] * 11,
    # Row for Mnemo_B = 2.0
    [
        100.0,
        96.4277,
        92.8554,
        89.2831,
        85.7108,
        82.1385,
        78.5662,
        74.9939,
        71.4216,
        67.8493,
        64.2770,
    ],
    # Row for Mnemo_B = 3.0
    [
        100.0,
        100.0,
        96.4277,
        92.8554,
        89.2831,
        85.7108,
        82.1385,
        78.5662,
        74.9939,
        71.4216,
        67.8493,
    ],
    # Row for Mnemo_B = 4.0
    [
        100.0,
        100.0,
        100.0,
        96.4277,
        92.8554,
        89.2831,
        85.7108,
        82.1385,
        78.5662,
        74.9939,
        71.4216,
    ],
]

MNEMO_B_VALUES = [1.0, 2.0, 3.0, 4.0]
MNEMO_C_VALUES = [0.1 * i for i in range(11)]  # 0.0 .. 1.0


# --- Internal helpers ---------------------------------------------------------


def _find_closest_index(value: float, grid: list[float]) -> int:
    """
    Return index of the grid value closest to 'value'.

    If two grid points are equally distant, the lower grid value is preferred.
    """
    closest_idx = 0
    min_diff = abs(grid[0] - value)
    for i, v in enumerate(grid[1:], start=1):
        diff = abs(v - value)
        if diff < min_diff:
            min_diff = diff
            closest_idx = i
        elif diff == min_diff and v > value:
            # value sits exactly in the middle: prefer the lower grid value
            break
    return closest_idx


def _get_tmn(mnemo_b: float, mnemo_c: float) -> float:
    """
    Fetch TMN from table based on Mnemo_B and Mnemo_C
    using nearest neighbours on the predefined grids.
    """
    # Clamp mnemo values into supported ranges
    mnemo_b = max(min(mnemo_b, max(MNEMO_B_VALUES)), min(MNEMO_B_VALUES))
    mnemo_c = max(min(mnemo_c, max(MNEMO_C_VALUES)), min(MNEMO_C_VALUES))

    idx_b = _find_closest_index(mnemo_b, MNEMO_B_VALUES)
    idx_c = _find_closest_index(mnemo_c, MNEMO_C_VALUES)

    # Safety: keep indices within table bounds
    idx_b = max(0, min(idx_b, len(TMN_TABLE) - 1))
    idx_c = max(0, min(idx_c, len(TMN_TABLE[0]) - 1))

    return TMN_TABLE[idx_b][idx_c]


def _calculate_methane_number_avl(composition: Dict[str, float]) -> float:
    """
    Core methane number calculation using a simplified AVL-style approach.

    Parameters
    ----------
    composition:
        Dict mapping component name -> mole/volume fraction (must be >= 0).
        Fractions do not need to be normalized; they are renormalized over
        recognised components.

    Returns
    -------
    float
        Estimated methane number.

    Raises
    ------
    ValueError
        If negative fractions are provided, or if no B/C components
        are present so the TMN table cannot be used.
    """
    if not composition:
        raise ValueError("Composition dictionary is empty.")

    # 1. Filter allowed components and normalise
    filtered: Dict[str, float] = {}
    for comp, mf in composition.items():
        if mf < 0.0:
            raise ValueError(
                f"Mole/volume fraction for '{comp}' must be non-negative "
                f"(got {mf})."
            )
        if comp not in ALLOWED_COMPONENTS:
            warnings.warn(
                f"Component '{comp}' is not supported by this AVL-based "
                f"method and will be ignored.",
                UserWarning,
            )
            continue
        filtered[comp] = mf

    if not filtered:
        raise ValueError("No recognised components in composition.")

    total = sum(filtered.values())
    if total <= 0.0:
        raise ValueError("Sum of recognised component fractions is zero.")

    for comp in filtered:
        filtered[comp] /= total

    # Split into groups
    group_a: Dict[str, float] = {}
    group_b: Dict[str, float] = {}
    group_c: Dict[str, float] = {}

    for comp, mf in filtered.items():
        if comp in GROUP_A:
            group_a[comp] = mf
        elif comp in GROUP_B:
            group_b[comp] = mf
        else:  # GROUP_C
            group_c[comp] = mf

    sum_b = sum(group_b.values())
    sum_c = sum(group_c.values())

    # Handle special case: almost pure methane
    if sum_b == 0.0 and sum_c == 0.0:
        if group_a.get("CH4", 0.0) > 0.99:
            return 100.0
        raise ValueError(
            "Composition contains no components from groups B or C; "
            "this simplified AVL method cannot be applied."
        )

    if sum_b <= 0.0 or sum_c <= 0.0:
        # You could implement more nuanced handling here if needed
        raise ValueError(
            "Composition must contain at least one Group B component "
            "(C3/C4) and one Group C component for this TMN-based AVL "
            "approximation."
        )

    # 2. Compute Mnemo_B and Mnemo_C as carbon-atom-weighted averages
    numerator_b = sum(mf * CARBON_ATOMS[comp] for comp, mf in group_b.items())
    numerator_c = sum(mf * CARBON_ATOMS[comp] for comp, mf in group_c.items())

    mnemo_b = numerator_b / sum_b
    mnemo_c = numerator_c / sum_c

    # 3. Look up TMN and weight by B*C fraction
    tmn_value = _get_tmn(mnemo_b, mnemo_c)
    total_mn = tmn_value * sum_b * sum_c

    # If B and C cover only part of the gas, you may want to blend this
    # with 100 for the remaining fraction. For now we just return the
    # contribution based on B and C interaction.
    return float(total_mn)


# --- Public API ---------------------------------------------------------------


def estimate_methane_number(composition: Dict[str, float]) -> float:
    """
    Estimate methane number of a gaseous fuel.

    This is a lightweight, TMN-table-based approximation inspired by
    the AVL method described in EN 16726:2015 Annex A. :contentReference[oaicite:2]{index=2}

    Parameters
    ----------
    composition:
        Dict mapping component name to mole/volume fraction.
        The following component keys are recognised (others are ignored
        with a warning):

        CH4, C2H6, C3H8, iC4H10, nC4H10,
        iC5H12, nC5H12, C6H14, C7plus,
        N2, CO2, H2S, H2O

    Returns
    -------
    float
        Estimated methane number.
    """
    return _calculate_methane_number_avl(composition)
