# core/components.py

from typing import Dict, Any
REQUIRED_KEYS = ["composition", "critical_properties", "heating_values"]

def validate_natural_gas_data(data: Dict[str, Any]) -> None:
    for key in REQUIRED_KEYS:
        if key not in data:
            raise ValueError(f"Missing key in natural_gas_data: {key}")

    comp = data["composition"]
    if not isinstance(comp, dict) or len(comp) == 0:
        raise ValueError("composition must be a non-empty dict")

    total = sum(comp.values())
    if abs(total - 1.0) > 1e-6:
        raise ValueError(f"Sum of mole fractions must be 1.0, got {total}")

    crit = data["critical_properties"]
    for comp_name in comp:
        if comp_name not in crit:
            raise ValueError(f"Missing critical_properties for component {comp_name}")
        if "molecular_weight" not in crit[comp_name]:
            raise ValueError(f"Missing molecular_weight for {comp_name}")

def get_molecular_weights(data: Dict[str, Any]) -> Dict[str, float]:
    """Return dict of molecular weights [g/mol] for all components."""
    crit = data["critical_properties"]
    return {name: props["molecular_weight"] for name, props in crit.items()}


def get_heating_values(data: Dict[str, Any]) -> Dict[str, Dict[str, float]]:
    """Return dict of heating values per component."""
    return data.get("heating_values", {})

