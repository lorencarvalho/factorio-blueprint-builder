---
name: factorio-blueprint-builder
description: Create and decode Factorio blueprints. Use this when the user asks to create a Factorio blueprint, design a factory layout, generate a blueprint string, or understand Factorio blueprint format.
---

# Factorio Blueprint Builder

A Claude plugin and skill for creating, decoding, and working with Factorio blueprints.

## Overview

Factorio is a factory-building automation game where players extract resources, design production chains, and automate manufacturing processes to build a rocket and escape an alien planet.

Blueprints let players save and replicate factory designs, enabling efficient scaling of production, sharing proven layouts with others, and avoiding repetitive manual construction of complex machine arrangements.

Factorio blueprints are encoded as base64 strings containing zlib-compressed JSON data. This skill helps you create valid blueprint strings that can be imported directly into Factorio.

## Typical workflow

Generally speaking, users will request that you create a Factorio blueprint to satisfy a particular need. Such as:

* Setting up starter base layouts (smelting arrays, mall production, science automation)
* Creating modular production cells for specific items (circuits, engines, science packs)
* Designing rail networks (intersections, stations, stackers)
* Building defensive perimeters (walls, turrets, laser arrays)
* Optimizing belt balancers and splitters
* Constructing solar panel arrays and power distribution
* Decoding existing blueprints to understand or modify them

Your role is to generate the JSON structure for the requested design, compress it with zlib, encode it to base64, and prefix it with version byte `0` to create a valid blueprint string.

## Blueprint Format

### Blueprint String Structure
1. Blueprint strings start with version byte `0` (for Factorio 1.1+)
2. Followed by base64-encoded, zlib-compressed JSON data
3. The JSON contains the blueprint definition

### Core JSON Structure

```json
{
  "blueprint": {
    "item": "blueprint",
    "label": "Blueprint Name",
    "version": 281479275806721,
    "icons": [
      {"signal": {"type": "item", "name": "item-name"}, "index": 1}
    ],
    "entities": [
      {
        "entity_number": 1,
        "name": "entity-name",
        "position": {"x": 0, "y": 0},
        "direction": 0
      }
    ]
  }
}
```

### Key Fields

- **version**: Game version encoded as 64-bit integer. Use `281479275806721` for Factorio 1.1
- **entities**: Array of entities in the blueprint
  - **entity_number**: Unique integer ID (starting from 1)
  - **name**: Internal entity name (e.g., "transport-belt", "assembling-machine-3")
  - **position**: Object with `x` and `y` coordinates (can be decimal)
  - **direction**: Rotation (0=North, 2=East, 4=South, 6=West)
  - **recipe**: Recipe name for assembling machines
  - **items**: Item requests for requester chests (object mapping item names to counts)
  - **connections**: Wiring connections for circuit network

## Common Entities

### Transport
- `transport-belt`, `fast-transport-belt`, `express-transport-belt`
- `underground-belt`, `fast-underground-belt`, `express-underground-belt`
- `splitter`, `fast-splitter`, `express-splitter`

### Production
- `assembling-machine-1`, `assembling-machine-2`, `assembling-machine-3`
- `chemical-plant`
- `oil-refinery`
- `electric-furnace`, `steel-furnace`, `stone-furnace`

### Logistics
- `inserter`, `fast-inserter`, `stack-inserter`, `long-handed-inserter`
- `wooden-chest`, `iron-chest`, `steel-chest`
- `logistic-chest-passive-provider`, `logistic-chest-active-provider`
- `logistic-chest-storage`, `logistic-chest-requester`, `logistic-chest-buffer`

### Power
- `small-electric-pole`, `medium-electric-pole`, `big-electric-pole`, `substation`
- `solar-panel`
- `accumulator`
- `steam-engine`, `steam-turbine`
- `boiler`, `heat-exchanger`, `nuclear-reactor`

### Defense
- `gun-turret`, `laser-turret`, `flamethrower-turret`
- `stone-wall`, `gate`
- `radar`

### Mining & Fluids
- `electric-mining-drill`, `burner-mining-drill`, `pumpjack`
- `pump`, `offshore-pump`
- `pipe`, `pipe-to-ground`
- `storage-tank`

## Creating Blueprint Strings

### Using Draftsman Library (Recommended)

This skill uses the **Draftsman** library, a Python package for creating and manipulating Factorio blueprints. 

Draftsman provides:
- **Automatic collision detection** - Warns when entities overlap
- **Built-in validation** - Catches invalid positions, recipes, and entity configurations
- **Coordinate handling** - Manages both tile positions and absolute positions automatically
- **Type safety** - Prevents common errors before blueprint generation

### Step-by-Step Process with Draftsman

1. **Create a blueprint** using `create_blueprint()`
2. **Add entities** with `add_entity()` - includes automatic validation
3. **Verify layout** by visualizing with `blueprint_to_ascii()`
4. **Validate** using `validate_blueprint()` to catch collisions
5. **Encode** to blueprint string with `encode_blueprint()`

### Using the Blueprint Utilities Script

The `scripts/blueprint_utils.py` module provides helper functions built on Draftsman:

#### As a Python Module

```python
from scripts.blueprint_utils import (
    create_blueprint, add_entity, encode_blueprint,
    decode_blueprint, validate_blueprint, blueprint_to_ascii
)

# Create a new blueprint
blueprint = create_blueprint("Iron Gear Production", "Produces iron gears")

# Add entities with automatic validation
add_entity(blueprint, "assembling-machine-2",
           tile_position=(0, 0),
           recipe="iron-gear-wheel")

add_entity(blueprint, "fast-inserter",
           tile_position=(1, -1),
           direction=4)  # South

# Validate for collisions and errors
if validate_blueprint(blueprint):
    print("Blueprint is valid!")

# Visualize the layout
print(blueprint_to_ascii(blueprint, show_coords=True))

# Encode to blueprint string
blueprint_string = encode_blueprint(blueprint)
```

#### As a CLI Tool

```bash
# Generate an example blueprint
python scripts/blueprint_utils.py example

# Create a new empty blueprint
python scripts/blueprint_utils.py create --label "My Blueprint" --output blueprint.txt

# Encode from JSON file
python scripts/blueprint_utils.py encode blueprint.json

# Decode a blueprint string
python scripts/blueprint_utils.py decode "0eNqrVkpJTc7PKy4p..." --pretty

# Visualize a blueprint with coordinates
python scripts/blueprint_utils.py visualize blueprint.json --coords
```

### Direct Draftsman Usage

For more complex blueprints, you can use Draftsman directly:

```python
from draftsman.blueprintable import Blueprint
from draftsman.entity import new_entity
from draftsman.constants import Direction

# Create blueprint
blueprint = Blueprint()
blueprint.label = "Complex Layout"
blueprint.version = (2, 0)

# Add entities directly
assembler = new_entity("assembling-machine-2")
assembler.tile_position = (0, 0)
assembler.recipe = "electronic-circuit"
blueprint.entities.append(assembler)

# Check for overlaps before adding
inserter = new_entity("fast-inserter")
inserter.tile_position = (1, -1)
inserter.direction = Direction.SOUTH

# Draftsman automatically warns if entities collide
blueprint.entities.append(inserter)

# Find entities in blueprint
machines = blueprint.find_entities_filtered(type="assembling-machine")
for machine in machines:
    print(f"Found {machine.name} at {machine.tile_position}")

# Validate and encode
blueprint.validate()
blueprint_string = blueprint.to_string(version=(2, 0))
```

## Best Practices

### Entity Positioning

**Use `tile_position` for grid-aligned entities** (recommended):
- Draftsman automatically calculates the correct center position
- Integer coordinates make spacing calculations easier
- Example: `tile_position=(0, 0)` for a 3x3 assembler centers it at (1.5, 1.5)

**Entity size reference**:
- **1x1 entities** (belts, inserters, poles): Center at (x+0.5, y+0.5)
- **2x2 entities**: Center at (x+1, y+1)
- **3x3 entities** (assemblers, furnaces): Center at (x+1.5, y+1.5)
- **5x5 entities** (chem plants, refineries): Center at (x+2.5, y+2.5)

**Spacing calculations**:
- Distance between entities = (size1/2) + (size2/2) + clearance
- Example: Two 3x3 assemblers with 1 tile gap = 1.5 + 1.5 + 1 = 4 tiles apart
- Inserters reach 1 tile from their center (long-handed reach 2 tiles)

**Direction constants**:
- `Direction.NORTH` or `0` = North (↑)
- `Direction.EAST` or `2` = East (→)
- `Direction.SOUTH` or `4` = South (↓)
- `Direction.WEST` or `6` = West (←)

### Validation and Error Prevention

1. **Always visualize** before encoding: Use `blueprint_to_ascii(blueprint, show_coords=True)`
2. **Check collisions**: Call `validate_blueprint()` to catch overlapping entities
3. **Use tile_position**: Prefer `tile_position` over absolute `position` for grid alignment
4. **Verify recipes**: Ensure recipe names match internal Factorio names (lowercase, hyphenated)
5. **Test incrementally**: Add entities one at a time and visualize frequently

## Example Blueprints

### Simple Belt Line

```json
{
  "blueprint": {
    "item": "blueprint",
    "label": "Simple Belt",
    "version": 281479275806721,
    "entities": [
      {"entity_number": 1, "name": "transport-belt", "position": {"x": 0, "y": 0}, "direction": 2},
      {"entity_number": 2, "name": "transport-belt", "position": {"x": 1, "y": 0}, "direction": 2},
      {"entity_number": 3, "name": "transport-belt", "position": {"x": 2, "y": 0}, "direction": 2}
    ]
  }
}
```

### Assembler with Inserters

```json
{
  "blueprint": {
    "item": "blueprint",
    "label": "Gear Assembler",
    "version": 281479275806721,
    "entities": [
      {"entity_number": 1, "name": "assembling-machine-2", "position": {"x": 0.5, "y": 0.5}, "recipe": "iron-gear-wheel"},
      {"entity_number": 2, "name": "inserter", "position": {"x": 0.5, "y": -1}, "direction": 4},
      {"entity_number": 3, "name": "inserter", "position": {"x": 0.5, "y": 2}, "direction": 0}
    ]
  }
}
```

## Workflow

When the user requests a blueprint, follow this process:

### 1. Understand Requirements
- What should the blueprint produce or do?
- What scale/size constraints exist?
- What tier of technology (basic/advanced/end-game)?

### 2. Plan Layout with Draftsman
```python
from scripts.blueprint_utils import create_blueprint, add_entity, blueprint_to_ascii

# Create blueprint
blueprint = create_blueprint("Production Cell", "Assembles iron gears")

# Start with core production building
add_entity(blueprint, "assembling-machine-2",
           tile_position=(0, 0),
           recipe="iron-gear-wheel")
```

### 3. Add Entities Incrementally
Add one entity at a time, visualizing after each addition:

```python
# Add input inserter
add_entity(blueprint, "fast-inserter",
           tile_position=(1, -1),
           direction=4)

# Visualize to verify placement
print(blueprint_to_ascii(blueprint, show_coords=True))

# Add more entities...
add_entity(blueprint, "fast-inserter",
           tile_position=(1, 3),
           direction=0)

# Visualize again
print(blueprint_to_ascii(blueprint, show_coords=True))
```

### 4. Validate for Collisions
```python
from scripts.blueprint_utils import validate_blueprint

if validate_blueprint(blueprint):
    print("✓ Blueprint is valid!")
else:
    print("✗ Validation errors detected - check output above")
```

### 5. Encode and Provide Output
```python
from scripts.blueprint_utils import encode_blueprint

blueprint_string = encode_blueprint(blueprint)

print("\n=== FINAL BLUEPRINT ===")
print(f"Label: {blueprint.label}")
print(f"\nBlueprint String:")
print(blueprint_string)
print(f"\nVisualization:")
print(blueprint_to_ascii(blueprint, show_coords=True))
print("\nCopy the blueprint string and paste it in Factorio!")
```

### Key Points
- **Use Draftsman helpers** from `blueprint_utils.py` - they handle validation automatically
- **Visualize frequently** with `blueprint_to_ascii()` to catch positioning errors early
- **Use tile_position** for all entity placement - it's easier to reason about
- **Validate before encoding** to catch collisions and invalid configurations
- **Provide both** the visualization and the blueprint string to the user

## Entity Positioning Guide

This section provides formulas and examples to help calculate correct entity positions.

### Common Entity Sizes

| Entity Type | Size | Tile Position Example | Absolute Center |
|------------|------|---------------------|-----------------|
| Belt, Inserter, Chest | 1×1 | (0, 0) | (0.5, 0.5) |
| Assembling Machine 1 | 3×3 | (0, 0) | (1.5, 1.5) |
| Assembling Machine 2/3 | 3×3 | (0, 0) | (1.5, 1.5) |
| Electric Furnace | 3×3 | (0, 0) | (1.5, 1.5) |
| Chemical Plant | 5×5 | (0, 0) | (2.5, 2.5) |
| Oil Refinery | 5×5 | (0, 0) | (2.5, 2.5) |

### Spacing Calculations

**Formula**: `distance = (size1 / 2) + (size2 / 2) + gap`

**Examples**:

1. **Assembler (3×3) to Inserter (1×1)** - adjacent, no gap:
   - Distance = 1.5 + 0.5 + 0 = 2 tiles
   - If assembler at tile (0, 0), inserter at tile (0, 2) or (2, 0)

2. **Two Assemblers (3×3)** - with 1 tile gap:
   - Distance = 1.5 + 1.5 + 1 = 4 tiles
   - If first at tile (0, 0), second at tile (4, 0)

3. **Assembler (3×3) to Chem Plant (5×5)** - with 2 tile gap:
   - Distance = 1.5 + 2.5 + 2 = 6 tiles
   - If assembler at tile (0, 0), chem plant at tile (6, 0)

### Inserter Positioning

Inserters pick up from behind and place in front, with 1-tile reach:

```python
# For a 3x3 assembler at tile (0, 0) which centers at (1.5, 1.5):

# North input inserter (facing south INTO assembler)
add_entity(blueprint, "inserter",
           tile_position=(1, -1),  # 1 tile north of assembler
           direction=4)  # SOUTH

# South output inserter (facing north OUT of assembler)
add_entity(blueprint, "inserter",
           tile_position=(1, 3),  # 1 tile south of assembler
           direction=0)  # NORTH

# East input inserter (facing west INTO assembler)
add_entity(blueprint, "inserter",
           tile_position=(3, 1),  # 1 tile east
           direction=6)  # WEST
```

### Power Pole Coverage

- Small electric pole: 7.5 tile radius (can reach 7-8 tiles)
- Medium electric pole: 9 tile radius
- Big electric pole: 30 tile radius
- Substation: 18 tile radius

**Tip**: Place poles every 6-7 tiles for small poles, every 16 tiles for medium poles.

## Tips

- **Always use Draftsman** - the automatic collision detection will save you from spacing errors
- **Visualize frequently** - use `blueprint_to_ascii(blueprint, show_coords=True)` after adding entities
- **Keep blueprints modular** and tileable when possible
- **Use descriptive labels** and icons
- **Test incrementally** - add a few entities, visualize, validate, repeat
- **Account for inserter reach** (1 tile) and belt throughput (Yellow=15/s, Red=30/s, Blue=45/s)
- **Consider power pole placement** for full coverage

## Resources

- Entity names: Check Factorio Wiki for exact internal names
- Recipes: Use Factorio's recipe names (lowercase, hyphenated)
- Grid alignment: Most buildings are 1×1, 2×2, 3×3, or 5×5
- Belt throughput: Yellow=15/s, Red=30/s, Blue=45/s
