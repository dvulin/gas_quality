"""
Methane Number Calculation Module
Based on EN 16726:2015 Annex A - AVL Method
"""

import warnings
from typing import Dict, List, Tuple

# Component groups according to EN 16726:2015, Annex A
GROUP_A = frozenset({"CH4", "C2H6"})
GROUP_B = frozenset({"C3H8", "iC4H10", "nC4H10"})
GROUP_C_COMPONENTS = frozenset({
    "iC5H12", "nC5H12", "C6H14", "C7plus",
    "N2", "CO2", "H2S", "H2O"
})
ALLOWED_COMPONENTS = GROUP_A | GROUP_B | GROUP_C_COMPONENTS

# Carbon atoms per component (C7plus approximated as 7 C atoms)
CARBON_ATOMS = {
    "CH4": 1, "C2H6": 2, "C3H8": 3,
    "iC4H10": 4, "nC4H10": 4,
    "iC5H12": 5, "nC5H12": 5,
    "C6H14": 6, "C7plus": 7,
    "N2": 0, "CO2": 1, "H2S": 0, "H2O": 0
}

# TMN table from EN 16726:2015, Annex A, Table A.2
# Rows: Mnemo_B [1.0, 2.0, 3.0, 4.0]
# Columns: Mnemo_C [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
TMN_TABLE = [
    [100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0],
    [100.0, 96.4277, 92.8554, 89.2831, 85.7108, 82.1385, 78.5662, 74.9939, 71.4216, 67.8493, 64.277],
    [100.0, 100.0, 96.4277, 92.8554, 89.2831, 85.7108, 82.1385, 78.5662, 74.9939, 71.4216, 67.8493],
    [100.0, 100.0, 100.0, 96.4277, 92.8554, 89.2831, 85.7108, 82.1385, 78.5662, 74.9939, 71.4216]
]

MNEMO_B_VALUES = [1.0, 2.0, 3.0, 4.0]
MNEMO_C_VALUES = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]

# Coefficients for A20 system (methane-CO2-N2)
A20_COEFFICIENTS = [
    [2.9917430E+02, -1.5119580E+01, -3.1156360E-01, 7.6359480E-01, 4.5480690E-02, 1.1230410E-02],
    [-2.3762630E-02, -7.1562940E-04, 6.5557090E-04, -2.1468550E-03, 4.3554940E-04, 3.8606680E-06],
    [1.3816990E-06, -7.9339020E-06, 6.6993640E-05, -4.6077260E-06, 2.6105700E-08, -6.1439140E-11],
    [-8.3693870E-07, 3.9280730E-09]
]


def _find_closest_index(value: float, value_list: List[float]) -> int:
    """Find the index of the closest value in the list."""
    closest_idx = 0
    min_diff = abs(value_list[0] - value)
    
    for i, v in enumerate(value_list):
        diff = abs(v - value)
        if diff < min_diff:
            min_diff = diff
            closest_idx = i
    
    return closest_idx


def _get_tmn(mnemo_b: float, mnemo_c: float) -> float:
    """
    Retrieve TMN from table based on Mnemo_B and Mnemo_C.
    Uses nearest neighbor if exact value is not in table.
    """
    idx_b = _find_closest_index(mnemo_b, MNEMO_B_VALUES)
    idx_c = _find_closest_index(mnemo_c, MNEMO_C_VALUES)
    
    # Constrain indices within table bounds
    idx_b = max(0, min(idx_b, len(TMN_TABLE) - 1))
    idx_c = max(0, min(idx_c, len(TMN_TABLE[0]) - 1))
    
    return TMN_TABLE[idx_b][idx_c]


def _calculate_mn_a20(x_ch4: float, y_co2: float) -> float:
    """
    Calculate methane number for A20 system (CH4-CO2-N2).
    
    Args:
        x_ch4: Methane content (% vol/vol)
        y_co2: CO2 content (% vol/vol)
    
    Returns:
        Methane number for the A20 mixture
    """
    coeffs = A20_COEFFICIENTS
    
    mn = 0.0
    for i in range(8):
        for j in range(7 - i):
            if i < len(coeffs) and j < len(coeffs[i]):
                mn += coeffs[i][j] * (x_ch4 ** i) * (y_co2 ** j)
    
    return mn


def estimate_methane_number(composition: Dict[str, float]) -> float:
    """
    Calculate methane number using the normative AVL method from EN 16726:2015, Annex A.
    
    Args:
        composition: Dictionary with component name (str) as key and mole fraction (float) as value.
                    Mole fractions should sum to 1.0 (or 100%) and must be >= 0.0.
                    Supported components: CH4, C2H6, C3H8, iC4H10, nC4H10, iC5H12, 
                    nC5H12, C6H14, C7plus, N2, CO2, H2S, H2O
    
    Returns:
        float: Calculated methane number (MN) according to AVL method.
    
    Raises:
        ValueError: If input composition is invalid (negative fractions, missing required components).
    
    Example:
        >>> composition = {'CH4': 0.85, 'C2H6': 0.06, 'C3H8': 0.03, 'N2': 0.03, 'CO2': 0.03}
        >>> mn = estimate_methane_number(composition)
    """
    # --- 1. Validation and component grouping ---
    group_a = {}
    group_b = {}
    group_c = {}
    
    for component, mole_fraction in composition.items():
        if mole_fraction < 0.0:
            raise ValueError(f"Mole fraction for component '{component}' must not be negative. Got: {mole_fraction}")
        
        if mole_fraction == 0.0:
            continue
        
        if component not in ALLOWED_COMPONENTS:
            warnings.warn(f"Component '{component}' is not allowed in AVL method and will be ignored.", UserWarning)
            continue
        
        if component in GROUP_A:
            group_a[component] = mole_fraction
        elif component in GROUP_B:
            group_b[component] = mole_fraction
        else:  # component in GROUP_C_COMPONENTS
            group_c[component] = mole_fraction
    
    # Check if required components are present
    if not group_b or not group_c:
        # Special case: pure or nearly pure methane
        if group_a and len(group_a) == 1 and "CH4" in group_a:
            return 100.0
        raise ValueError("Composition must contain components from both Group B and Group C for AVL method.")
    
    # --- 2. Calculate Mnemo_B and Mnemo_C ---
    sum_b = sum(group_b.values())
    sum_c = sum(group_c.values())
    
    if sum_b <= 0.0 or sum_c <= 0.0:
        raise ValueError("Composition must contain components from both Group B and Group C for basic AVL iteration.")
    
    numerator_b = sum(mf * CARBON_ATOMS[comp] for comp, mf in group_b.items())
    numerator_c = sum(mf * CARBON_ATOMS[comp] for comp, mf in group_c.items())
    
    mnemo_b = numerator_b / sum_b
    mnemo_c = numerator_c / sum_c
    
    # --- 3. Iterative process and final MN calculation ---
    total_mn = 0.0
    for comp_b, y_b in group_b.items():
        for comp_c, y_c in group_c.items():
            tmn_value = _get_tmn(mnemo_b, mnemo_c)
            total_mn += y_b * y_c * tmn_value
    
    # Methane number of simplified mixture
    mn_prime = total_mn
    
    # --- 4. Correction for inerts (N2 and CO2) ---
    # Calculate sum of combustible components
    sum_combustibles = sum(group_a.values()) + sum(group_b.values())
    n2_fraction = composition.get("N2", 0.0)
    co2_fraction = composition.get("CO2", 0.0)
    
    # Create nitrogen-free mixture for A20 calculation
    total_for_a20 = sum_combustibles + co2_fraction
    
    if total_for_a20 > 0:
        x_ch4_a20 = (sum_combustibles / total_for_a20) * 100.0
        y_co2_a20 = (co2_fraction / total_for_a20) * 100.0
        
        mn_inerts = _calculate_mn_a20(x_ch4_a20, y_co2_a20)
        mn_methane = 100.0003  # Pure methane MN
        
        # Final correction
        mn = mn_prime + mn_inerts - mn_methane
    else:
        mn = mn_prime
    
    return round(mn, 2)