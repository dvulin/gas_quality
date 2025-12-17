# core/mixing_rules.py

from typing import Dict

M_AIR = 28.96  # g/mol, approx.

def calc_mixture_molar_mass(
    composition: Dict[str, float],
    molecular_weights: Dict[str, float],
) -> float:
    """
    Return molar mass of the gas mixture [g/mol].
    """
    M_mix = 0.0
    for comp, z in composition.items():
        Mw = molecular_weights.get(comp)
        if Mw is None:
            raise ValueError(f"No molecular weight for component {comp}")
        M_mix += z * Mw
    return M_mix


def calc_relative_density(M_mix: float, M_air: float = M_AIR) -> float:
    """
    Relative density d = M_mix / M_air.
    """
    return M_mix / M_air


def normalize_composition(composition: Dict[str, float]) -> Dict[str, float]:
    """
    Normalize mole fractions to sum = 1.0 (in case of small rounding errors).
    """
    total = sum(composition.values())
    if total <= 0:
        raise ValueError("Total composition must be > 0")
    return {k: v / total for k, v in composition.items()}
