# 6x6x6 Grid Layout with 2 Bots

## Grid Coordinates
- **X-axis**: 0 to 5 (6 positions)
- **Y-axis**: 0 to 5 (6 positions)  
- **Z-axis**: 0 to 5 (6 positions)

## Bot Positions
- **Bot 1**: Position (5, 5, 1) - Top right corner, Z=1
- **Bot 2**: Position (5, 5, 4) - Top right corner, Z=4

## Visual Representation

### Top View (Z=0 to Z=5)
```
Y=5  ┌─────────────────┐
      │                 │
      │                 │
      │                 │
      │                 │
      │                 │
      │              🤖 │ ← Bot 1 (Z=1), Bot 2 (Z=4)
Y=0   └─────────────────┘
       X=0            X=5
```

### Side View (X=5, Y=5)
```
Z=5  ┌─┐
      │ │
Z=4  │🤖│ ← Bot 2
      │ │
Z=3  │ │
      │ │
Z=2  │ │
      │ │
Z=1  │🤖│ ← Bot 1
      │ │
Z=0  └─┘
```

## Movement Constraints
- Bots can only move in X and Y directions (horizontal plane)
- Z coordinate remains fixed for each bot
- Grid boundaries: 0 ≤ X ≤ 5, 0 ≤ Y ≤ 5
- Bots return to (5, 5) after completing orders

## Pathfinding
- A* algorithm calculates optimal paths within 6x6 grid
- Bots avoid obstacles (currently none set)
- Movement: Up, Down, Left, Right (no diagonal)

## Status Flow
1. **Idle**: Bots at (5, 5) waiting for orders
2. **Moving**: Bots traveling to destination bins
3. **Packing**: Bots at destination collecting items
4. **Returning**: Bots moving back to (5, 5)
5. **Idle**: Bots back at (5, 5) ready for next order 