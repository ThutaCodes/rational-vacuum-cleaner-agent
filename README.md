# Rational Vacuum Cleaner Agent

[![Hacktoberfest](https://img.shields.io/badge/Hacktoberfest-2025-blue)](https://hacktoberfest.com/)

This project simulates a rational vacuum cleaner agent in a 4x4 grid world using Python and Pygame.

## Features
- Visual simulation of a vacuum agent cleaning dirt in a grid environment
- Agent uses simple logic to clean all dirt and return home
- Scrollable action history panel
- Adjustable speed and manual/auto modes

## Controls
- `SPACE`: Step manually
- `A`: Toggle auto mode
- `UP/DOWN`: Change speed
- `R`: Reset simulation
- `Mouse Wheel` or `W/S` or `PageUp/PageDown`: Scroll recent actions

## Requirements
- Python 3.x
- pygame (see `requirement.txt`)

## How to Run
1. (Optional) Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirement.txt
   ```
3. Run the simulation:
   ```bash
   python3 agent.py
   ```

## PEAS Description
- **Performance**: Clean all dirt, return home, minimize energy
- **Environment**: 4x4 grid world with dirt in some locations
- **Actuators**: Move (N,S,E,W), Suck dirt, Empty bag
- **Sensors**: Detect dirt, Detect location, Detect bag capacity

## Example

| Percept Sequence | Action      |
|------------------|------------|
| [A, Clean]       | Move East  |
| [A, Dirty]       | Suck       |
| [D, Dirty]       | Suck       |
| [D, Clean]       | Move South |

---

Feel free to modify the agent logic or UI for your own experiments!

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to contribute.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
