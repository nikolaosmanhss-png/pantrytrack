# Licensing and Business Model

## Chosen license: MIT

| Option considered | Type | Why not / why |
|---|---|---|
| GPL-3.0 | Strong copyleft | Protects freedom of derivatives, but some businesses and integrators avoid it because modified versions they distribute must also be GPL |
| Apache-2.0 | Permissive + patent grant | Good choice, but longer and more complex than this small project needs |
| **MIT** | Permissive | **Chosen.** Short, widely understood, compatible with almost every other licence and allows commercial use – which is what small businesses and integrators need |

All dependencies are compatible with MIT:

| Dependency | License |
|---|---|
| Python / sqlite3 | PSF License / SQLite is public domain |
| pandas | BSD-3-Clause |
| Matplotlib | Matplotlib License (PSF-based, BSD-compatible) |
| pytest (development only) | MIT |

Contributions are accepted under the same licence ("inbound = outbound"), as stated in CONTRIBUTING.md.

## Business model

PantryTrack follows a **community open-source + paid services** model:

1. **Free core** – the tool is and stays free under MIT.
2. **Services** – setup, data import from existing spreadsheets, staff training and custom reports for businesses that do not have technical staff.
3. **Hosted version (future)** – a paid, managed web version for owners who do not want to install anything.
4. **Sponsorship** – GitHub Sponsors for individuals and businesses that rely on the tool.

The open licence lowers the adoption barrier, while services generate income from the users who value convenience over doing it themselves.
