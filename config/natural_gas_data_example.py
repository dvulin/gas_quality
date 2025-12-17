# config/natural_gas_data_example.py

natural_gas_data = {
    "composition": {
        "CH4": 0.85,
        "C2H6": 0.06,
        "C3H8": 0.03,
        "iC4H10": 0.006,
        "nC4H10": 0.006,
        "iC5H12": 0.002,
        "nC5H12": 0.002,
        "C6H14": 0.001,
        "C7plus": 0.001,
        "N2": 0.03,
        "CO2": 0.012,
        "H2S": 0.00,
        "H2O": 0.00,
    },
    "critical_properties": {
         "CH4": {
            "name": "Methane",
            "formula": "CH4",
            "molecular_weight": 16.04,           # g/mol [citation:1][citation:7]
            "critical_temperature": 190.7,       # K [citation:3]
            "critical_pressure": 45.8,           # bar [citation:3] (converted from atm)
            "boiling_point": -161.5,             # °C [citation:1]
        },
        "C2H6": {
            "name": "Ethane",
            "formula": "C2H6",
            "molecular_weight": 30.07,           # g/mol [citation:7]
            "critical_temperature": 305.48,      # K [citation:3]
            "critical_pressure": 48.20,          # bar [citation:3] (converted from atm)
            "boiling_point": -88.6,              # °C [citation:1]
        },
        "C3H8": {
            "name": "Propane",
            "formula": "C3H8",
            "molecular_weight": 44.01,           # g/mol [citation:7] (Note: Same as CO2)
            "critical_temperature": 370.01,      # K [citation:3]
            "critical_pressure": 42.1,           # bar [citation:3] (converted from atm)
            "boiling_point": -42.1,              # °C [citation:6]
        },
"iC4H10": {
            "name": "Isobutane",
            "formula": "iC4H10",
            "molecular_weight": 58.12,           # g/mol [citation:1][citation:7]
            "critical_temperature": 408.15,      # K (135°C converted) [citation:1]
            "critical_pressure": 37.2,           # bar [citation:1]
            "boiling_point": -11.7,              # °C [citation:1]
        },
         "nC4H10": {
            "name": "n-Butane",
            "formula": "nC4H10",
            "molecular_weight": 58.12,           # g/mol [citation:7]
            "critical_temperature": 425.17,      # K [citation:3]
            "critical_pressure": 37.47,          # bar [citation:3] (converted from atm)
            "boiling_point": 31.0,               # °F = -0.56°C [citation:8]
        },
        "iC5H12": {
            "name": "Isopentane",
            "formula": "iC5H12",
            "molecular_weight": 72.15,           # g/mol [citation:7]
            "critical_temperature": 828.77,      # R = 460.43 K (converted) [citation:7]
            "critical_pressure": 490.4,          # psia = 33.81 bar (converted) [citation:7]
            "boiling_point": 27.9,               # °C (estimated typical value)
        },
        "nC5H12": {
            "name": "n-Pentane",
            "formula": "nC5H12",
            "molecular_weight": 72.15,           # g/mol [citation:7]
            "critical_temperature": 845.37,      # R = 469.65 K (converted) [citation:7]
            "critical_pressure": 488.6,          # psia = 33.69 bar (converted) [citation:7]
            "boiling_point": 36.1,               # °C (estimated typical value)
        },
        "C6H14": {
            "name": "n-Hexane",
            "formula": "C6H14",
            "molecular_weight": 86.18,           # g/mol [citation:7]
            "critical_temperature": 913.37,      # R = 507.43 K (converted) [citation:7]
            "critical_pressure": 436.9,          # psia = 30.12 bar (converted) [citation:7]
            "boiling_point": 68.7,               # °C [citation:1]
        },
        "C7plus": {
            "name": "n-Heptane (C7+ representative)",
            "formula": "C7H16",
            "molecular_weight": 100.20,          # g/mol (estimated for heptane)
            "critical_temperature": 540.0,       # K (estimated)
            "critical_pressure": 27.0,           # bar (estimated)
            "boiling_point": 98.4,               # °C (estimated for heptane)
        },
        "N2": {
            "name": "Nitrogen",
            "formula": "N2",
            "molecular_weight": 28.01,           # g/mol [citation:7]
            "critical_temperature": 126.2,       # K [citation:3]
            "critical_pressure": 33.54,          # bar [citation:3] (converted from atm)
            "boiling_point": -195.8,             # °C (estimated from -320.4°F) [citation:1]
        },
        "CO2": {
            "name": "Carbon Dioxide",
            "formula": "CO2",
            "molecular_weight": 44.01,           # g/mol [citation:1][citation:7]
            "critical_temperature": 304.20,      # K [citation:3]
            "critical_pressure": 72.90,          # bar [citation:3] (converted from atm)
            "boiling_point": -78.4,              # °C (sublimation point) [citation:1]
        },
        "H2S": {
            "name": "Hydrogen Sulfide",
            "formula": "H2S",
            "molecular_weight": 34.08,           # g/mol [citation:1][citation:7]
            "critical_temperature": 373.53,      # K (100.4°C converted) [citation:1]
            "critical_pressure": 91.9,           # bar [citation:1]
            "boiling_point": -60.3,              # °C [citation:1]
        },
        "H2O": {
            "name": "Water",
            "formula": "H2O",
            "molecular_weight": 18.02,           # g/mol
            "critical_temperature": 647.27,      # K [citation:3]
            "critical_pressure": 218.167,        # bar [citation:3] (converted from atm)
            "boiling_point": 100.0,              # °C
        },
    },
    "heating_values": {
        "CH4": {"HHV": 53.28, "LHV": 47.91},
        "C2H6": {"HHV": 68.19, "LHV": 62.47},
        "C3H8": {"HHV": 81.07, "LHV": 74.54},
        "iC4H10": {"HHV": 91.96, "LHV": 84.71},
        "nC4H10": {"HHV": 92.32, "LHV": 85.08},
        # ostale komponente možeš dodati kasnije (ili koristiti aproksimacije)
    },
    "wobbe_index": {
        "CH4": {"upper": 53.28, "lower": 47.91},
        "C2H6": {"upper": 68.19, "lower": 62.47},
        "C3H8": {"upper": 81.07, "lower": 74.54},
        "iC4H10": {"upper": 91.96, "lower": 84.71},
        "nC4H10": {"upper": 92.32, "lower": 85.08},
    },
}
