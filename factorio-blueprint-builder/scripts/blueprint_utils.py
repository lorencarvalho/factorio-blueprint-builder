#!/usr/bin/env python3
"""
Factorio Blueprint Utilities

This script provides functions to create, encode, decode, and visualize Factorio blueprints
using the Draftsman library. It can be used standalone or imported as a module.

Usage:
    # Create a new blueprint programmatically
    python blueprint_utils.py create --label "My Blueprint" --output my_blueprint.txt

    # Decode a blueprint string
    python blueprint_utils.py decode "0eNqrVkpJTc7PKy4p..." --output blueprint.json

    # Encode a JSON file to blueprint string
    python blueprint_utils.py encode blueprint.json

    # Visualize a blueprint as ASCII art
    python blueprint_utils.py visualize blueprint.json
    python blueprint_utils.py visualize "0eNqrVkpJTc7PKy4p..."

    # Generate an example blueprint with visualization
    python blueprint_utils.py example

    # Use as a module
    from blueprint_utils import create_blueprint, add_entity, encode_blueprint, decode_blueprint
"""

import json
import sys
import argparse
import io
from typing import Dict, Any, Optional, Tuple, Union

try:
    from draftsman.blueprintable import Blueprint
    from draftsman.entity import new_entity
    from draftsman.constants import Direction, ValidationMode
    from draftsman.validators import set_mode
    DRAFTSMAN_AVAILABLE = True
except ImportError:
    DRAFTSMAN_AVAILABLE = False
    print("Warning: factorio-draftsman not installed. Install with: pip install factorio-draftsman", file=sys.stderr)

# Ensure UTF-8 output for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def create_blueprint(label: str = "New Blueprint", description: str = "", version: Tuple[int, int] = (2, 0)) -> 'Blueprint':
    """
    Create a new Factorio blueprint using Draftsman.

    Args:
        label: Blueprint name/label
        description: Blueprint description
        version: Factorio version tuple (major, minor)

    Returns:
        Blueprint object that can be modified and encoded
    """
    if not DRAFTSMAN_AVAILABLE:
        raise ImportError("Draftsman library is required. Install with: pip install factorio-draftsman")

    blueprint = Blueprint()
    blueprint.label = label
    blueprint.description = description
    blueprint.version = version

    return blueprint


def add_entity(blueprint: 'Blueprint',
               entity_name: str,
               position: Optional[Tuple[float, float]] = None,
               tile_position: Optional[Tuple[int, int]] = None,
               direction: Union[int, 'Direction'] = 0,
               recipe: Optional[str] = None,
               **kwargs) -> 'Blueprint':
    """
    Add an entity to a blueprint with automatic validation and collision detection.

    Args:
        blueprint: Blueprint object to add entity to
        entity_name: Internal Factorio entity name (e.g., "assembling-machine-2")
        position: Absolute position (x, y) as floats (entity center)
        tile_position: Tile position (x, y) as integers (top-left corner)
        direction: Direction constant or integer (0=North, 2=East, 4=South, 6=West)
        recipe: Recipe name for assembling machines/furnaces
        **kwargs: Additional entity-specific parameters

    Returns:
        The blueprint object (for method chaining)

    Raises:
        Warning if entities overlap (OverlappingObjectsWarning)
    """
    if not DRAFTSMAN_AVAILABLE:
        raise ImportError("Draftsman library is required")

    # Create entity
    entity = new_entity(entity_name, **kwargs)

    # Set position (prefer tile_position for grid alignment)
    if tile_position is not None:
        entity.tile_position = tile_position
    elif position is not None:
        entity.position = position
    else:
        entity.tile_position = (0, 0)

    # Set direction
    entity.direction = direction

    # Set recipe if applicable
    if recipe and hasattr(entity, 'recipe'):
        entity.recipe = recipe

    # Add to blueprint (Draftsman will warn about overlaps)
    blueprint.entities.append(entity)

    return blueprint


def validate_blueprint(blueprint: 'Blueprint', pedantic: bool = True) -> bool:
    """
    Validate a blueprint for errors and warnings.

    Args:
        blueprint: Blueprint to validate
        pedantic: If True, enables strict validation mode with warnings

    Returns:
        True if valid, False otherwise
    """
    if not DRAFTSMAN_AVAILABLE:
        raise ImportError("Draftsman library is required")

    try:
        if pedantic:
            with set_mode(ValidationMode.PEDANTIC):
                blueprint.validate()
        else:
            blueprint.validate()
        return True
    except Exception as e:
        print(f"Validation error: {e}", file=sys.stderr)
        return False


def encode_blueprint(blueprint: Union['Blueprint', Dict[str, Any]], version: Tuple[int, int] = (2, 0)) -> str:
    """
    Encode a blueprint to a Factorio blueprint string.

    Args:
        blueprint: Blueprint object or dictionary
        version: Factorio version tuple (default: 2.0)

    Returns:
        Encoded blueprint string that can be imported into Factorio
    """
    if not DRAFTSMAN_AVAILABLE:
        raise ImportError("Draftsman library is required")

    if isinstance(blueprint, dict):
        # Create Blueprint from dictionary
        blueprint = Blueprint.from_dict(blueprint)

    return blueprint.to_string(version=version)


def decode_blueprint(blueprint_string: str) -> Dict[str, Any]:
    """
    Decode a Factorio blueprint string to a dictionary.

    Args:
        blueprint_string: Encoded blueprint string from Factorio

    Returns:
        Dictionary containing the decoded blueprint data
    """
    if not DRAFTSMAN_AVAILABLE:
        raise ImportError("Draftsman library is required")

    blueprint = Blueprint.from_string(blueprint_string)
    return blueprint.to_dict()


def get_blueprint_dimensions(blueprint: Union['Blueprint', Dict[str, Any]]) -> Tuple[int, int]:
    """
    Get the dimensions of a blueprint in tiles.

    Args:
        blueprint: Blueprint object or dictionary

    Returns:
        Tuple of (width, height) in tiles
    """
    if not DRAFTSMAN_AVAILABLE:
        raise ImportError("Draftsman library is required")

    if isinstance(blueprint, dict):
        blueprint = Blueprint.from_dict(blueprint)

    dimensions = blueprint.get_dimensions()
    return dimensions


def get_entity_count(blueprint: Union['Blueprint', Dict[str, Any]]) -> Dict[str, int]:
    """
    Count entities in a blueprint by type.

    Args:
        blueprint: Blueprint object or dictionary

    Returns:
        Dictionary mapping entity names to counts
    """
    if not DRAFTSMAN_AVAILABLE:
        raise ImportError("Draftsman library is required")

    if isinstance(blueprint, dict):
        blueprint = Blueprint.from_dict(blueprint)

    counts = {}
    for entity in blueprint.entities:
        name = entity.name
        counts[name] = counts.get(name, 0) + 1

    return counts


# Entity to ASCII character mapping
ENTITY_ASCII_MAP = {
    'transport-belt': {
        0: '^',  # North
        2: '>',  # East
        4: 'v',  # South
        6: '<',  # West
    },
    'fast-transport-belt': {
        0: '▲',
        2: '►',
        4: '▼',
        6: '◄',
    },
    'express-transport-belt': {
        0: '⇧',
        2: '⇨',
        4: '⇩',
        6: '⇦',
    },
    'underground-belt': {
        0: '⊼',  # North
        2: '⊿',  # East
        4: '⊽',  # South
        6: '⊾',  # West
    },
    'splitter': 'Y',
    'inserter': 'i',
    'long-handed-inserter': 'I',
    'fast-inserter': 'f',
    'stack-inserter': 'S',
    'assembling-machine-1': '①',
    'assembling-machine-2': '②',
    'assembling-machine-3': '③',
    'electric-furnace': 'F',
    'stone-furnace': 'f',
    'steel-furnace': 'F',
    'electric-mining-drill': 'M',
    'burner-mining-drill': 'm',
    'pumpjack': 'P',
    'offshore-pump': 'W',
    'pipe': '│',
    'pipe-to-ground': '╤',
    'storage-tank': 'T',
    'small-electric-pole': '┼',
    'medium-electric-pole': '╬',
    'big-electric-pole': '▓',
    'substation': '█',
    'solar-panel': '☼',
    'accumulator': 'A',
    'boiler': 'B',
    'steam-engine': 'E',
    'steam-turbine': 'T',
    'nuclear-reactor': '☢',
    'heat-exchanger': 'H',
    'lab': 'L',
    'radar': 'R',
    'roboport': '☁',
    'logistic-chest-passive-provider': 'p',
    'logistic-chest-active-provider': 'P',
    'logistic-chest-storage': 'S',
    'logistic-chest-buffer': 'B',
    'logistic-chest-requester': 'R',
    'wooden-chest': 'c',
    'iron-chest': 'C',
    'steel-chest': 'C',
    'gun-turret': 't',
    'laser-turret': 'T',
    'flamethrower-turret': 'F',
    'stone-wall': '#',
    'gate': '=',
}


def blueprint_to_ascii(blueprint_data: Union['Blueprint', Dict[str, Any]],
                       padding: int = 1,
                       show_legend: bool = True,
                       show_coords: bool = False) -> str:
    """
    Convert a blueprint to ASCII art representation.

    Args:
        blueprint_data: Blueprint object or dictionary
        padding: Number of empty cells to add around the blueprint
        show_legend: Whether to show a legend of entities
        show_coords: Whether to show coordinate axes

    Returns:
        String containing ASCII art representation of the blueprint
    """
    # Convert Blueprint object to dict if needed
    if DRAFTSMAN_AVAILABLE and isinstance(blueprint_data, Blueprint):
        blueprint_data = blueprint_data.to_dict()

    # Extract the blueprint (handle both direct blueprint and blueprint book)
    bp = blueprint_data.get('blueprint', blueprint_data)

    if not bp or 'entities' not in bp:
        return "No entities found in blueprint"

    entities = bp['entities']

    if not entities:
        return "Blueprint is empty"

    # Find bounds
    min_x = min(e['position']['x'] for e in entities)
    max_x = max(e['position']['x'] for e in entities)
    min_y = min(e['position']['y'] for e in entities)
    max_y = max(e['position']['y'] for e in entities)

    # Calculate grid size with padding
    width = int(max_x - min_x) + 1 + (padding * 2)
    height = int(max_y - min_y) + 1 + (padding * 2)

    # Create empty grid
    grid = [[' ' for _ in range(width)] for _ in range(height)]

    # Track entity types used
    entities_used = {}

    # Place entities on grid
    for entity in entities:
        x = int(entity['position']['x'] - min_x) + padding
        y = int(entity['position']['y'] - min_y) + padding
        name = entity['name']
        direction = entity.get('direction', 0)

        # Get ASCII character for this entity
        char = '?'
        entity_map = ENTITY_ASCII_MAP.get(name)

        if isinstance(entity_map, dict):
            char = entity_map.get(direction, '?')
        elif entity_map:
            char = entity_map

        # Place on grid
        if 0 <= y < height and 0 <= x < width:
            grid[y][x] = char

        # Track entity usage
        if name not in entities_used:
            entities_used[name] = char

    # Build output
    output = []

    # Add label if present
    if 'label' in bp:
        output.append(f"Blueprint: {bp['label']}")
        output.append("")

    # Add coordinate header if requested
    if show_coords:
        # Calculate coordinate range
        coord_min_x = int(min_x)
        coord_max_x = int(max_x)

        # Create coordinate header
        coord_header = "    "
        for x in range(coord_min_x - padding, coord_max_x + padding + 1):
            coord_header += f"{x:>3}"
        output.append(coord_header)

    # Add the ASCII grid
    output.append("    ┌" + "─" * width + "┐")
    for i, row in enumerate(grid):
        if show_coords:
            # Calculate actual Y coordinate
            y_coord = int(min_y) - padding + i
            output.append(f"{y_coord:>3} │" + "".join(row) + "│")
        else:
            output.append("    │" + "".join(row) + "│")
    output.append("    └" + "─" * width + "┘")

    # Add legend
    if show_legend and entities_used:
        output.append("")
        output.append("Legend:")
        for name, char in sorted(entities_used.items()):
            output.append(f"  {char} = {name}")

    return "\n".join(output)


def create_simple_example() -> 'Blueprint':
    """Create a simple example blueprint using Draftsman."""
    if not DRAFTSMAN_AVAILABLE:
        raise ImportError("Draftsman library is required")

    blueprint = create_blueprint("Simple Production Line", "Example of assembler with inserters")

    # Add assembling machine in the center
    add_entity(blueprint, "assembling-machine-2",
               tile_position=(0, 0),
               recipe="iron-gear-wheel")

    # Add input inserter (north side)
    add_entity(blueprint, "fast-inserter",
               tile_position=(1, -1),
               direction=Direction.SOUTH)

    # Add output inserter (south side)
    add_entity(blueprint, "fast-inserter",
               tile_position=(1, 3),
               direction=Direction.NORTH)

    # Add power pole
    add_entity(blueprint, "small-electric-pole",
               tile_position=(4, 1))

    # Add input belt
    for i in range(3):
        add_entity(blueprint, "transport-belt",
                   tile_position=(1, -4 + i),
                   direction=Direction.SOUTH)

    # Add output belt
    for i in range(3):
        add_entity(blueprint, "transport-belt",
                   tile_position=(1, 4 + i),
                   direction=Direction.SOUTH)

    return blueprint


def main():
    """Command-line interface."""
    if not DRAFTSMAN_AVAILABLE:
        print("Error: factorio-draftsman is not installed.", file=sys.stderr)
        print("Install with: pip install factorio-draftsman", file=sys.stderr)
        sys.exit(1)

    parser = argparse.ArgumentParser(
        description='Create, encode, and decode Factorio blueprints using Draftsman'
    )
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # Create command
    create_parser = subparsers.add_parser('create', help='Create a new blueprint')
    create_parser.add_argument('--label', default='New Blueprint', help='Blueprint label')
    create_parser.add_argument('--description', default='', help='Blueprint description')
    create_parser.add_argument('-o', '--output', help='Output file (default: stdout)')

    # Encode command
    encode_parser = subparsers.add_parser('encode', help='Encode JSON to blueprint string')
    encode_parser.add_argument('input', help='JSON file to encode')
    encode_parser.add_argument('-o', '--output', help='Output file (default: stdout)')

    # Decode command
    decode_parser = subparsers.add_parser('decode', help='Decode blueprint string to JSON')
    decode_parser.add_argument('input', help='Blueprint string to decode')
    decode_parser.add_argument('-o', '--output', help='Output file (default: stdout)')
    decode_parser.add_argument('--pretty', action='store_true', help='Pretty-print JSON')

    # Visualize command
    visualize_parser = subparsers.add_parser('visualize', help='Display blueprint as ASCII art')
    visualize_parser.add_argument('input', help='Blueprint string or JSON file to visualize')
    visualize_parser.add_argument('--padding', type=int, default=1, help='Padding around blueprint (default: 1)')
    visualize_parser.add_argument('--no-legend', action='store_true', help='Hide entity legend')
    visualize_parser.add_argument('--coords', action='store_true', help='Show coordinate axes')

    # Example command
    subparsers.add_parser('example', help='Generate an example blueprint')

    args = parser.parse_args()

    if args.command == 'create':
        # Create new blueprint
        blueprint = create_blueprint(args.label, args.description)
        blueprint_string = encode_blueprint(blueprint)

        # Output
        if args.output:
            with open(args.output, 'w') as f:
                f.write(blueprint_string)
            print(f"Blueprint string written to {args.output}")
        else:
            print(blueprint_string)

    elif args.command == 'encode':
        # Read JSON file
        with open(args.input, 'r') as f:
            blueprint_data = json.load(f)

        # Encode using Draftsman
        blueprint_string = encode_blueprint(blueprint_data)

        # Output
        if args.output:
            with open(args.output, 'w') as f:
                f.write(blueprint_string)
            print(f"Blueprint string written to {args.output}")
        else:
            print(blueprint_string)

    elif args.command == 'decode':
        # Decode using Draftsman
        blueprint_data = decode_blueprint(args.input)

        # Output
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(blueprint_data, f, indent=2 if args.pretty else None)
            print(f"Blueprint JSON written to {args.output}")
        else:
            if args.pretty:
                print(json.dumps(blueprint_data, indent=2))
            else:
                print(json.dumps(blueprint_data))

    elif args.command == 'visualize':
        # Determine if input is a file or blueprint string
        blueprint_data = None

        try:
            # Try to read as file first
            with open(args.input, 'r') as f:
                blueprint_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # Not a file or not JSON, try as blueprint string
            try:
                blueprint_data = decode_blueprint(args.input)
            except Exception as e:
                print(f"Error: Could not parse input as file or blueprint string: {e}")
                sys.exit(1)

        # Generate ASCII art
        ascii_art = blueprint_to_ascii(
            blueprint_data,
            padding=args.padding,
            show_legend=not args.no_legend,
            show_coords=args.coords
        )
        print(ascii_art)

    elif args.command == 'example':
        # Create example using Draftsman
        blueprint = create_simple_example()

        print("Example Blueprint:")
        print(f"Label: {blueprint.label}")
        print(f"Description: {blueprint.description}")
        print(f"Entities: {len(blueprint.entities)}")
        print()

        # Get entity counts
        counts = get_entity_count(blueprint)
        print("Entity counts:")
        for name, count in sorted(counts.items()):
            print(f"  {name}: {count}")
        print()

        # Encode to string
        blueprint_string = encode_blueprint(blueprint)

        print("Blueprint String:")
        print(blueprint_string)
        print("\nASCII Visualization:")
        print(blueprint_to_ascii(blueprint, show_coords=True))
        print("\nCopy the blueprint string above and paste it in Factorio!")

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
