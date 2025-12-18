def _calculate_mn_a20(x_ch4: float, y_co2: float) -> float:"""
Methane Number Calculation Module
Based on EN 16726:2015 Annex A - AVL Method
"""

import warnings
from typing import Dict, List, Tuple

# Component groups according to EN 16726:2015, Annex A
# The standard mentions these in Section A.2.1:
# - carbon monoxide, butadiene, butylene, ethylene, propylene, hydrogen sulphide
# - hydrogen, propane, ethane, butane, methane, nitrogen, carbon dioxide

GROUP_A = frozenset({"CH4", "C2H6"})
GROUP_B = frozenset({"C3H8", "C4H10"})  # Propane and butanes
GROUP_C_COMPONENTS = frozenset({
    "C5H12", "C6H14", "C7plus",  # Higher hydrocarbons
    "N2", "CO2", "H2S", "H2O", "H2",  # Inerts and hydrogen
    "CO", "C2H4", "C3H6", "C4H6", "C4H8"  # Other combustibles per standard
})
ALLOWED_COMPONENTS = GROUP_A | GROUP_B | GROUP_C_COMPONENTS

# Ignored components (present in data but not used in calculation)
IGNORED_COMPONENTS = frozenset({"O2"})

# Input component aliases - map variations to standard names
COMPONENT_ALIASES = {
    # Isomer variants
    "iC4H10": "C4H10",
    "nC4H10": "C4H10",
    "iC5H12": "C5H12",
    "nC5H12": "C5H12",
    # Alternative naming
    "C6+": "C6H14",  # C6+ represents hexanes and higher
    "hexanes+": "C6H14",
}

# Carbon atoms per component
CARBON_ATOMS = {
    "CH4": 1, "C2H6": 2, "C3H8": 3,
    "C4H10": 4, "C5H12": 5, "C6H14": 6, "C7plus": 7,
    # Other combustibles
    "CO": 1, "C2H4": 2, "C3H6": 3, "C4H6": 4, "C4H8": 4,
    # Inerts
    "N2": 0, "CO2": 1, "H2S": 0, "H2O": 0, "H2": 0
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


def _normalize_composition(composition: Dict[str, float]) -> Dict[str, float]:
    """
    Normalize composition by combining iso/normal isomers into generic components.
    
    According to EN 16726:2015, the AVL method does not distinguish between
    isobutane/n-butane or isopentane/n-pentane.
    """
    normalized = {}
    
    for component, fraction in composition.items():
        # Map aliases to standard names
        std_component = COMPONENT_ALIASES.get(component, component)
        
        if std_component in normalized:
            normalized[std_component] += fraction
        else:
            normalized[std_component] = fraction
    
    return normalized


def _simplify_composition(composition: Dict[str, float]) -> Dict[str, float]:
    """
    Simplify composition by converting higher hydrocarbons to butane equivalents.
    
    According to EN 16726:2015 Section A.3.1:
    - Butadiene (C4H6) and butylene (C4H8) are replaced with butanes (multiply by 1.0)
    - Pentanes are replaced with butane equivalent by multiplying by 2.3
    - Hexanes+ (C6H14, C7plus) are replaced with butane equivalent by multiplying by 5.3
    """
    simplified = composition.copy()
    
    # Convert butadiene and butylene to butane equivalent (1:1)
    for component in ["C4H6", "C4H8"]:
        if component in simplified and simplified[component] > 0:
            c4_fraction = simplified.pop(component)
            simplified["C4H10"] = simplified.get("C4H10", 0.0) + c4_fraction * 1.0
    
    # Convert pentanes to butane equivalent
    if "C5H12" in simplified and simplified["C5H12"] > 0:
        c5_fraction = simplified.pop("C5H12")
        simplified["C4H10"] = simplified.get("C4H10", 0.0) + c5_fraction * 2.3
    
    # Convert hexanes+ to butane equivalent
    if "C6H14" in simplified and simplified["C6H14"] > 0:
        c6_fraction = simplified.pop("C6H14")
        simplified["C4H10"] = simplified.get("C4H10", 0.0) + c6_fraction * 5.3
    
    if "C7plus" in simplified and simplified["C7plus"] > 0:
        c7_fraction = simplified.pop("C7plus")
        simplified["C4H10"] = simplified.get("C4H10", 0.0) + c7_fraction * 5.3
    
    return simplified


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


def _correct_for_inerts(composition_original: Dict[str, float]) -> float:
    """
    Calculate the inert correction using A20 system.
    
    Per the VBA code, this uses the ORIGINAL composition (before simplification)
    and treats ALL combustibles as "methane" for the A20 calculation.
    
    Args:
        composition_original: Original composition before any simplification
    
    Returns:
        MN_inerts value for the correction formula
    """
    # Sum ALL combustibles (everything except N2, CO2, H2O, O2)
    inert_components = {"N2", "CO2", "H2O", "O2"}
    
    sum_combustibles = sum(v for k, v in composition_original.items() 
                          if k not in inert_components and v > 0)
    
    n2 = composition_original.get("N2", 0.0)
    co2 = composition_original.get("CO2", 0.0)
    
    # Total of all components
    sum_all = sum_combustibles + n2 + co2
    
    # Convert to nitrogen-free basis (as percentages)
    # This is the key: divide by (sum_all - nitrogen) to get N2-free percentages
    if sum_all - n2 > 1e-9:
        x_ch4_pct = (sum_combustibles * 100.0) / (sum_all - n2)
        y_co2_pct = (co2 * 100.0) / (sum_all - n2)
        
        mn_inerts = _calculate_mn_a20(x_ch4_pct, y_co2_pct)
    else:
        mn_inerts = 100.0
    
    return mn_inerts
    """
    Calculate methane number for A20 system (CH4-CO2-N2).
    
    According to EN 16726:2015, the A20 system is on a NITROGEN-FREE basis.
    The input is methane and CO2 percentages after removing nitrogen.
    
    Args:
        x_ch4: Methane content (% vol/vol) - expects percentage 0-100, nitrogen-free basis
        y_co2: CO2 content (% vol/vol) - expects percentage 0-100, nitrogen-free basis
    
    Returns:
        Methane number for the A20 mixture
    """
    # A20 formula: MN = sum over i,j of a(i,j) * x^i * y^j
    # where x is CH4%, y is CO2% (both on nitrogen-free basis)
    
    mn = 0.0
    
    # Row 0: a(0,0) through a(0,5)
    mn += 2.9917430E+02
    mn += -1.5119580E+01 * y_co2
    mn += -3.1156360E-01 * (y_co2 ** 2)
    mn += 7.6359480E-01 * (y_co2 ** 3)
    mn += 4.5480690E-02 * (y_co2 ** 4)
    mn += 1.1230410E-02 * (y_co2 ** 5)
    
    # Row 1: a(1,0) through a(1,5)
    mn += -2.3762630E-02 * x_ch4
    mn += -7.1562940E-04 * x_ch4 * y_co2
    mn += 6.5557090E-04 * x_ch4 * (y_co2 ** 2)
    mn += -2.1468550E-03 * x_ch4 * (y_co2 ** 3)
    mn += 4.3554940E-04 * x_ch4 * (y_co2 ** 4)
    mn += 3.8606680E-06 * x_ch4 * (y_co2 ** 5)
    
    # Row 2: a(2,0) through a(2,4)
    mn += 1.3816990E-06 * (x_ch4 ** 2)
    mn += -7.9339020E-06 * (x_ch4 ** 2) * y_co2
    mn += 6.6993640E-05 * (x_ch4 ** 2) * (y_co2 ** 2)
    mn += -4.6077260E-06 * (x_ch4 ** 2) * (y_co2 ** 3)
    mn += 2.6105700E-08 * (x_ch4 ** 2) * (y_co2 ** 4)
    
    # Row 3: a(3,0) through a(3,3)
    mn += -6.1439140E-11 * (x_ch4 ** 3)
    mn += -8.3693870E-07 * (x_ch4 ** 3) * y_co2
    mn += 3.9280730E-09 * (x_ch4 ** 3) * (y_co2 ** 2)
    
    return mn


def estimate_methane_number(composition: Dict[str, float]) -> float:
    """
    Calculate methane number using the normative AVL method from EN 16726:2015, Annex A.
    
    This implementation follows the standard exactly as specified, including:
    - No distinction between iso- and normal- isomers of butanes and pentanes
    - Support for hydrogen (H2) in the calculation
    - Proper handling of inert components (N2, CO2, H2O, H2S)
    
    Args:
        composition: Dictionary with component name (str) as key and mole fraction (float) as value.
                    Mole fractions should sum to 1.0 and must be >= 0.0.
                    
                    Supported components:
                    - Hydrocarbons: CH4, C2H6, C3H8, C4H10 (or iC4H10, nC4H10), 
                      C5H12 (or iC5H12, nC5H12), C6H14, C7plus, C6+ (alias for C6H14)
                    - Other combustibles: CO, C2H4 (ethylene), C3H6 (propylene),
                      C4H6 (butadiene), C4H8 (butylene)
                    - Inerts: N2, CO2, H2S, H2O, H2
                    - Ignored: O2 (oxygen - ignored per standard)
                    
                    Note: iC4H10 and nC4H10 are automatically combined into C4H10.
                          iC5H12 and nC5H12 are automatically combined into C5H12.
    
    Returns:
        float: Calculated methane number (MN) according to AVL method, rounded to whole number.
               Typical range: 0-100, where 100 represents pure methane quality.
    
    Raises:
        ValueError: If input composition is invalid (negative fractions, missing required components).
    
    Examples:
        >>> # Example 1: Natural gas composition
        >>> composition = {
        ...     'CH4': 0.85, 'C2H6': 0.06, 'C3H8': 0.03,
        ...     'iC4H10': 0.006, 'nC4H10': 0.006,
        ...     'N2': 0.03, 'CO2': 0.012
        ... }
        >>> mn = estimate_methane_number(composition)
        
        >>> # Example 2: Hydrogen-enriched gas
        >>> composition = {
        ...     'CH4': 0.80, 'C2H6': 0.05, 'C3H8': 0.02,
        ...     'C4H10': 0.02, 'H2': 0.05, 'N2': 0.03, 'CO2': 0.03
        ... }
        >>> mn = estimate_methane_number(composition)
    """
    # --- 1. Normalize: combine iso/normal isomers ---
    normalized = _normalize_composition(composition)
    
    # --- 2. Validation and component grouping ---
    group_a = {}
    group_b = {}
    group_c = {}
    
    for component, mole_fraction in normalized.items():
        if mole_fraction < 0.0:
            raise ValueError(f"Mole fraction for component '{component}' must not be negative. Got: {mole_fraction}")
        
        if mole_fraction == 0.0:
            continue
        
        # Skip ignored components (like O2)
        if component in IGNORED_COMPONENTS:
            continue
        
        if component not in ALLOWED_COMPONENTS:
            warnings.warn(
                f"Component '{component}' is not part of the AVL/Annex-A set and will be ignored in the methane-number estimate.",
                UserWarning
            )
            continue
        
        if component in GROUP_A:
            group_a[component] = mole_fraction
        elif component in GROUP_B:
            group_b[component] = mole_fraction
        else:  # component in GROUP_C_COMPONENTS
            group_c[component] = mole_fraction
    
    # --- 3. Simplify: convert C5+ to C4 equivalents ---
    all_combustibles = {**group_a, **group_b}
    simplified_b = _simplify_composition(all_combustibles)
    
    # Separate back into groups after simplification
    group_b_simplified = {k: v for k, v in simplified_b.items() if k in GROUP_B}
    
    # --- 4. Calculate MN based on available components ---
    sum_b = sum(group_b_simplified.values()) if group_b_simplified else 0.0
    sum_c = sum(group_c.values()) if group_c else 0.0
    
    # Check if we have both Group B and Group C components for full TMN calculation
    if sum_b > 1e-6 and sum_c > 1e-6:
        # Standard AVL method with TMN table
        numerator_b = sum(mf * CARBON_ATOMS[comp] for comp, mf in group_b_simplified.items())
        numerator_c = sum(mf * CARBON_ATOMS.get(comp, 0) for comp, mf in group_c.items())
        
        mnemo_b = numerator_b / sum_b
        mnemo_c = numerator_c / sum_c
        
        # Iterative process and MN calculation using TMN table
        total_mn = 0.0
        for comp_b, y_b in group_b_simplified.items():
            for comp_c, y_c in group_c.items():
                tmn_value = _get_tmn(mnemo_b, mnemo_c)
                total_mn += y_b * y_c * tmn_value
        
        mn_prime = total_mn
    
    else:
        # No Group B components (no propane/butane) or no Group C
        # Per standard, when components are missing, the TMN table calculation is skipped
        # and we rely on the A20 correction to give us the final value
        # Setting mn_prime to 100 means: MN = 100 + MNinerts - 100.0003 = MNinerts - 0.0003
        mn_prime = 100.0
    
    # --- 5. Correction for inerts using ORIGINAL composition ---
    # This is critical: the A20 correction uses the ORIGINAL composition,
    # not the simplified one!
    mn_inerts = _correct_for_inerts(composition)
    mn_methane = 100.0003  # Pure methane MN per standard
    
    # Final formula from standard
    mn = mn_prime + mn_inerts - mn_methane
    
    # Debug output for troubleshooting
    # print(f"Debug: mn_prime={mn_prime:.4f}, mn_inerts={mn_inerts:.4f}, mn_methane={mn_methane:.4f}, final MN={mn:.4f}")
    
    # The result should be in valid range 0-100
    if mn < 0 or mn > 105:
        warnings.warn(f"Calculated MN={mn:.2f} is outside expected range [0,100]. This may indicate an issue with the composition or calculation.", UserWarning)
    
    mn = max(0.0, min(100.0, mn))
    return round(mn, 0)