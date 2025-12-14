# Phase II — Connect Four (Minimax vs Alpha-Beta)

This project implements Connect Four from scratch and includes:
- Game environment (state, actions, transition, terminal test)
- Minimax and Alpha-Beta Pruning agents (depth-limited, heuristic evaluation)
- Human vs AI console play
- Required outputs for Phase II:
  - Partial game tree (DOT + JSON trace)
  - Highlighted pruned branches for Alpha-Beta (DOT + JSON trace)
  - Board snapshots after each move (text files)
  - Minimax vs Alpha-Beta decision difference diagram (DOT + text summary)
  - Performance comparison metrics (time, nodes expanded, depth reached, efficiency)

## Standard library only
- Uses only Python standard library.
- Visualization is exported as `.dot` (Graphviz) and `.txt/.json`.
  - If you have Graphviz installed, render diagrams with:
    `dot -Tpng outputs/tree_alphabeta.dot -o outputs/tree_alphabeta.png`

## Quick start
### 1) Play Human vs AI
```bash
python main.py --ai alphabeta --depth 5
```

### 2) Generate Phase II artifacts (comparison + diagrams)
```bash
python compare.py --depth 5 --trace-depth 3
```

Outputs are written to `outputs/`.
