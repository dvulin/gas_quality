# -*- coding: utf-8 -*-
"""
Created on Wed Dec 17 19:37:16 2025

@author: domagoj
"""

# example_run.py
from config.natural_gas_data_example import natural_gas_data
from iolib.load_input import load_hr_limits
from iolib.reporting import print_summary
from core.components import validate_natural_gas_data, get_molecular_weights, get_heating_values
from core.mixing_rules import calc_mixture_molar_mass, calc_relative_density, normalize_composition
from calc.heating_value import mixture_HHV_LHV_MJm3, MJm3_to_kWhm3
from calc.wobbe import wobbe_index
from calc.methane_number import estimate_methane_number
from calc.gas_quality_checks import (
    check_composition_limits,
    check_energy_and_wobbe,
    check_methane_number,
)

import os


def main():
    # 1. Validate and normalize input
    validate_natural_gas_data(natural_gas_data)
    composition = normalize_composition(natural_gas_data["composition"])
    molecular_weights = get_molecular_weights(natural_gas_data)
    heating_values = get_heating_values(natural_gas_data)

    # 2. Mixture properties
    M_mix = calc_mixture_molar_mass(composition, molecular_weights)
    d = calc_relative_density(M_mix)

    # 3. Energetics
    HHV_MJm3, LHV_MJm3 = mixture_HHV_LHV_MJm3(composition, heating_values)
    HHV_kWhm3 = MJm3_to_kWhm3(HHV_MJm3)
    LHV_kWhm3 = MJm3_to_kWhm3(LHV_MJm3)

    # 4. Wobbe indices (convert to kWh/m3)
    Wg_MJm3, Wd_MJm3 = wobbe_index(HHV_MJm3, LHV_MJm3, d)
    Wg_kWhm3 = MJm3_to_kWhm3(Wg_MJm3)
    Wd_kWhm3 = MJm3_to_kWhm3(Wd_MJm3)

    # 5. Methane number estimate
    MN = estimate_methane_number(composition)

    # 6. Load HR standard limits
    here = os.path.dirname(os.path.abspath(__file__))
    limits_path = os.path.join(here, "config", "hr_standard_limits.json")
    limits = load_hr_limits(limits_path)

    # 7. Checks
    check_comp = check_composition_limits(composition, limits)
    check_energy = check_energy_and_wobbe(
        HHV_kWhm3, LHV_kWhm3, Wg_kWhm3, Wd_kWhm3, d, limits
    )
    check_MN = check_methane_number(MN, limits)

    # Merge all check dicts
    all_checks = {**check_comp, **check_energy, **check_MN}

    # 8. Report
    print_summary(
        composition,
        HHV_kWhm3,
        LHV_kWhm3,
        Wg_kWhm3,
        Wd_kWhm3,
        d,
        MN,
        all_checks,
    )


if __name__ == "__main__":
    main()
