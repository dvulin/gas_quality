
import json
from typing import Dict, Any
import csv


def load_composition_from_json(path: str) -> Dict[str, float]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    # expects {"composition": {...}}
    comp = data.get("composition")
    if comp is None:
        raise ValueError("JSON file must contain 'composition' key")
    return {k: float(v) for k, v in comp.items()}


def load_composition_from_csv(path: str) -> Dict[str, float]:
    """
    CSV format:
    component,mole_fraction
    CH4,0.85
    ...
    """
    comp: Dict[str, float] = {}
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["component"].strip()
            z = float(row["mole_fraction"])
            comp[name] = z
    return comp


def load_hr_limits(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
