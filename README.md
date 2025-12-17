# gas_quality
module to estimate gas quality parameters (LHV, HHV, MN, Wobbe index) from given composition)

## Regulatory References

- **NN 158/13** — *Standardna kvaliteta prirodnog plina* (Croatian national standard)
  - Min CH₄: 85 mol%, Max CO₂: 2.5%, Max N₂: 7%
  - HHV: 10.28–12.75 kWh/m³
  - Wobbe: 12.75–15.81 kWh/m³ (upper), 11.48–14.23 (lower)
  - Relative density: 0.56–0.70

- **HERA Amendment (2021)** — *Prijedlog izmjena i dopuna Općih uvjeta opskrbe plinom*
  - Introduces **Methane Number ≥ 75** (CEN EN 16726)
  - Updates Wobbe min to 13.6 kWh/m³
  - HHV min raised to 10.96 kWh/m³

- **CEN EN 16726** — *Gas infrastructure - Quality of gas - Group H*
  - European standard for methane number (engine knock resistance)
  - Official method: engine test or approved correlation

- **EC 2015/703** — *Commission Regulation on energy labelling*
  - Framework for gas quality and capacity reservation

## ⚠️ Limitations & Notes
1. **Methane Number:** Official CEN EN 16726 requires engine test or validated AVL correlation.
2. **Reference Conditions:** Assumes 0°C / 25°C (or similar) for HHV/LHV. See HERA amendment for 15°C → 0°C conversion (coefficient 0.901).
3. **Dew Point, Sulfur Speciation:** Not yet implemented. Can be added as future modules.
4. **No External Dependencies:** Uses only Python stdlib (typing, json, csv). Extensible for `numpy`, `scipy` (future).

## Roadmap

- [ ] Implement full CEN EN 16726 methane number calculation
- [ ] Add dew point calculations (water, HC condensation)
- [ ] Temperature/pressure normalization utilities
- [ ] Sulfur speciation (H₂S, COS, RSH breakdown)
- [ ] Web API (FastAPI)
- [ ] Interactive GUI (Streamlit)
- [ ] Database backend (PostgreSQL, historical lab data)
- [ ] Gas blending optimizer

## 📝 License

No License

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/my-feature`)
3. Commit changes (`git commit -am 'Add my feature'`)
4. Push branch (`git push origin feature/my-feature`)
5. Open Pull Request

For major changes, please open an issue first.

## Contact

**Project Maintainer:** [domagoj vulin]  

Questions? Open an [issue](https://github.com/yourusername/natural-gas-analysis/issues).


