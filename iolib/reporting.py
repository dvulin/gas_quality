# io/reporting.py

from typing import Dict, Any


def print_summary(
    composition: Dict[str, float],
    HHV_kWhm3: float,
    LHV_kWhm3: float,
    Wg_kWhm3: float,
    Wd_kWhm3: float,
    rel_density: float,
    methane_number: float,
    checks: Dict[str, Dict[str, Any]],
) -> None:
    print("=== Natural Gas Mixture Summary ===")
    print("Composition (mol %):")
    for comp, z in composition.items():
        print(f"  {comp:8s}: {z * 100:7.3f}")

    print("\nEnergetics and Wobbe:")
    print(f"  HHV: {HHV_kWhm3:.3f} kWh/m3")
    print(f"  LHV: {LHV_kWhm3:.3f} kWh/m3")
    print(f"  Wg : {Wg_kWhm3:.3f} kWh/m3")
    print(f"  Wd : {Wd_kWhm3:.3f} kWh/m3")
    print(f"  d  : {rel_density:.4f}")
    print(f"  Methane number (est.): {methane_number:.1f}")

    print("\nCompliance check (HR standard):")
    any_fail = False
    for name, res in checks.items():
        status = res["status"]
        value = res["value"]
        vmin = res["min"]
        vmax = res["max"]
        print(
            f"  {name:20s}: {value:.4f} (min={vmin}, max={vmax}) -> {status}"
        )
        if status != "OK":
            any_fail = True

    if any_fail:
        print("\nResult: GAS DOES NOT MEET HR STANDARD on some parameters.")
    else:
        print("\nResult: GAS MEETS HR STANDARD (within checked parameters).")
