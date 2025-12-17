from typing import Dict, Tuple


def mixture_HHV_LHV_MJm3(
    composition: Dict[str, float],
    heating_values: Dict[str, Dict[str, float]],
) -> Tuple[float, float]:
    """
    Calculate mixture HHV and LHV [MJ/m3] from component volumetric HHV/LHV.

    Assumes provided HHV/LHV are per unit volume at same reference conditions,
    so linear mixing by mole fraction is acceptable.
    """
    HHV = 0.0
    LHV = 0.0
    for comp, z in composition.items():
        hv = heating_values.get(comp)
        if hv is None:
            # You may choose to ignore or raise; here we ignore silently
            continue
        HHV_i = hv.get("HHV", 0.0)
        LHV_i = hv.get("LHV", 0.0)
        HHV += z * HHV_i
        LHV += z * LHV_i
    return HHV, LHV


def MJm3_to_kWhm3(H_MJm3: float) -> float:
    return H_MJm3 / 3.6


def kWhm3_to_MJm3(H_kWhm3: float) -> float:
    return H_kWhm3 * 3.6
