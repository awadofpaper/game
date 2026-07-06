# 2D Open World RPG Game

A modular, content-rich, grind-focused 2D open world RPG built with Python and pygame. Features a massive 10,000x10,000 static world, breakable resources, skill trees, leveling, inventory, crafting, and full control and performance customization. Supports English, Spanish, and French. All graphics are simple colored rectangles for maximum clarity and extensibility.

## Features
- 10,000 x 10,000 static tile world (single file)
- Breakable rocks (groups), trees, and grass
- Resource drops: rubble, sticks, wood, ash, fiber (≤8% drop rate)
- Magic and burning mechanics
- Skill tree, leveling, inventory, crafting
- Health, stamina, and mana bars
- In-game overlay menus (main, pause, inventory, skill tree)
- Full control rebinding and customization
- Performance and accessibility options
- Save/load world and player state
- English, Spanish, French localization
- Single player only

## Getting Started
1. Install Python 3.8+
2. Install pygame: `pip install pygame`
3. Run the game: `python main.py`

## Project Structure
- main.py: Game entry point
- world.py: World data and logic
- player.py: Player logic
- entities.py: NPCs, monsters, objects
- graphics.py: Rendering and UI
- config.py: Settings and constants
- utils.py: Helper functions
- localization/: Language files

## License
MIT License
