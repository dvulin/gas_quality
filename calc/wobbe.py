from typing import Tuple


def wobbe_index(HHV: float, LHV: float, relative_density: float) -> Tuple[float, float]:
    """
    Calculate upper and lower Wobbe index from HHV/LHV and relative density.

    Inputs HHV, LHV in same units (e.g. MJ/m3), relative_density dimensionless.
    Output Wg, Wd u istim jedinicama kao ulaz (npr. MJ/m3).
    """
    if relative_density <= 0:
        raise ValueError("relative_density must be > 0")
    sqrt_d = relative_density ** 0.5
    Wg = HHV / sqrt_d
    Wd = LHV / sqrt_d
    return Wg, Wd
