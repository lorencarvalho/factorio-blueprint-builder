# Factorio Blueprint Builder

A Claude Code skill for creating and working with Factorio blueprints. This plugin enables Claude to help you design factory layouts, generate blueprint strings, and understand the Factorio blueprint format.

## Features

- Create Factorio blueprints from natural language descriptions
- Generate valid blueprint strings that can be imported directly into Factorio
- Decode existing blueprint strings to understand their contents
- Design complex factory layouts with proper entity placement
- Support for all common Factorio entities (belts, assemblers, inserters, etc.)
- Best practices for factory design and optimization
- Standalone Python utility script for encoding/decoding blueprints

## Installation

### Method 1: Local Installation (Development)

TBD

### Method 2: Project-Specific Installation

TBD

## Usage

Once installed, Claude will automatically use the Factorio Blueprint Builder skill when you ask questions or make requests related to Factorio blueprints.

### Example Requests

**Create a simple belt line:**
```
Create a Factorio blueprint for 10 express belts in a row going east
```

**Build a production setup:**
```
Create a blueprint for an iron gear wheel production setup with 4 assemblers,
input and output belts, and inserters
```

**Decode a blueprint:**
```
Decode this Factorio blueprint string and tell me what it contains:
0eNqrVkrKKU0tKMrMK1GyqlbKLEnNVbJCEtNRKk4tKcnMSy9WsiorL...
```

**Design a larger factory:**
```
Design a green circuit production line that takes in copper and iron plates
and outputs green circuits. Include proper ratios.
```
