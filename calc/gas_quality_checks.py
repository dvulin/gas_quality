from typing import Dict, Any


def check_range(name: str, value: float, limits: Dict[str, float]) -> Dict[str, Any]:
    """
    Generic range checker.
    """
    vmin = limits.get("min", None)
    vmax = limits.get("max", None)

    status = "OK"
    if vmin is not None and value < vmin:
        status = "LOW"
    if vmax is not None and value > vmax:
        status = "HIGH"

    return {
        "name": name,
        "value": value,
        "min": vmin,
        "max": vmax,
        "status": status,
    }


def check_composition_limits(
    composition: Dict[str, float],
    limits: Dict[str, Dict[str, float]],
) -> Dict[str, Dict[str, Any]]:
    """
    Check CO2, N2, O2 mol % against limits.
    """
    results = {}

    CO2 = composition.get("CO2", 0.0) * 100.0
    N2 = composition.get("N2", 0.0) * 100.0
    O2 = composition.get("O2", 0.0) * 100.0  # ako je prisutno

    if "CO2_mol_pct" in limits:
        results["CO2_mol_pct"] = check_range(
            "CO2_mol_pct", CO2, limits["CO2_mol_pct"]
        )
    if "N2_mol_pct" in limits:
        results["N2_mol_pct"] = check_range(
            "N2_mol_pct", N2, limits["N2_mol_pct"]
        )
    if "O2_mol_pct" in limits:
        results["O2_mol_pct"] = check_range(
            "O2_mol_pct", O2, limits["O2_mol_pct"]
        )

    return results


def check_energy_and_wobbe(
    HHV_kWhm3: float,
    LHV_kWhm3: float,
    Wg_kWhm3: float,
    Wd_kWhm3: float,
    rel_density: float,
    limits: Dict[str, Dict[str, float]],
) -> Dict[str, Dict[str, Any]]:
    results = {}
    if "HHV_kWhm3" in limits:
        results["HHV_kWhm3"] = check_range(
            "HHV_kWhm3", HHV_kWhm3, limits["HHV_kWhm3"]
        )
    if "LHV_kWhm3" in limits:
        results["LHV_kWhm3"] = check_range(
            "LHV_kWhm3", LHV_kWhm3, limits["LHV_kWhm3"]
        )
    if "Wobbe_HHV_kWhm3" in limits:
        results["Wobbe_HHV_kWhm3"] = check_range(
            "Wobbe_HHV_kWhm3", Wg_kWhm3, limits["Wobbe_HHV_kWhm3"]
        )
    if "Wobbe_LHV_kWhm3" in limits:
        results["Wobbe_LHV_kWhm3"] = check_range(
            "Wobbe_LHV_kWhm3", Wd_kWhm3, limits["Wobbe_LHV_kWhm3"]
        )
    if "relative_density" in limits:
        results["relative_density"] = check_range(
            "relative_density", rel_density, limits["relative_density"]
        )
    return results


def check_methane_number(
    methane_number: float,
    limits: Dict[str, Dict[str, float]],
) -> Dict[str, Dict[str, Any]]:
    results = {}
    if "methane_number" in limits:
        results["methane_number"] = check_range(
            "methane_number", methane_number, limits["methane_number"]
        )
    return results
