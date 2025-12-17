from typing import Dict


# Pseudo methane numbers per pure component (rough engineering estimates)
PSEUDO_MN = {
    "CH4": 100.0,
    "C2H6": 50.0,
    "C3H8": 35.0,
    "iC4H10": 30.0,
    "nC4H10": 30.0,
    "iC5H12": 25.0,
    "nC5H12": 25.0,
    "C6H14": 20.0,
    "C7plus": 15.0,
    "N2": 120.0,   # inert (diluent) podiže MN
    "CO2": 120.0,  # inert (diluent)
    "H2S": 80.0,   # vrlo gruba aproksimacija
    "H2O": 150.0,  # praktički inert
}


def estimate_methane_number(composition: Dict[str, float]) -> float:
    """
    Crude estimate of methane number using linear blending of pseudo MN values.

    MN_mix = sum(z_i * MN_i) / sum(z_i_with_MN)

    Ovo NIJE zamjena za službene metode (AVL / engine test), ali je korisno
    za brzu provjeru da li je plin grubo iznad / ispod zahtjeva MN >= 75.
    """
    num = 0.0
    den = 0.0
    for comp, z in composition.items():
        MN_i = PSEUDO_MN.get(comp)
        if MN_i is None:
            # Ignoriraj komponente bez definiranog pseudo MN
            continue
        num += z * MN_i
        den += z
    if den <= 0:
        raise ValueError("No components with defined pseudo methane number")
    return num / den
