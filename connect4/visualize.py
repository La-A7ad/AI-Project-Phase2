\
from __future__ import annotations
import os
import json
from typing import List
from .search import SearchTracer, TraceNode
from .game import ConnectFour

def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)

def save_snapshot(game: ConnectFour, out_dir: str, move_index: int, title: str = "") -> str:
    ensure_dir(out_dir)
    fname = os.path.join(out_dir, f"move_{move_index:02d}.txt")
    with open(fname, "w", encoding="utf-8") as f:
        if title:
            f.write(title + "\n\n")
        f.write(game.to_ascii() + "\n")
        f.write("\nLast move: " + game.pretty_last_move() + "\n")
    return fname

def tracer_to_json(tracer: SearchTracer, path: str) -> None:
    data = [n.__dict__ for n in tracer.nodes]
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def tracer_to_dot(tracer: SearchTracer, path: str, title: str = "Search Tree") -> None:
    """
    Write a Graphviz DOT file (no external Python libs).
    PRUNED nodes are styled in dashed red.
    """
    def label(n: TraceNode) -> str:
        mv = "root" if n.move is None else f"c{n.move}"
        p = "X" if n.turn_player == 1 else "O"
        v = "?" if n.value is None else str(n.value)
        if n.kind == "PRUNED":
            return f"{mv}\\nPRUNED\\nα={n.alpha}\\nβ={n.beta}"
        if n.alpha is None or n.beta is None:
            return f"{mv}\\n{n.kind}\\nturn={p}\\nv={v}"
        return f"{mv}\\n{n.kind}\\nturn={p}\\nv={v}\\nα={n.alpha}\\nβ={n.beta}"

    lines: List[str] = []
    lines.append("digraph G {")
    lines.append("  rankdir=TB;")
    lines.append('  labelloc="t";')
    lines.append(f'  label="{title}";')
    lines.append("  node [shape=box, fontsize=10];")

    for n in tracer.nodes:
        attrs = []
        if n.kind == "PRUNED" or n.pruned:
            attrs.append('style="dashed"')
            attrs.append('color="red"')
        elif n.kind == "MAX":
            attrs.append('color="blue"')
        elif n.kind == "MIN":
            attrs.append('color="black"')

        attr_str = ""
        if attrs:
            attr_str = ", " + ", ".join(attrs)

        lines.append(f'  n{n.id} [label="{label(n)}"{attr_str}];')

    for n in tracer.nodes:
        if n.parent is None:
            continue
        edge_attrs = ""
        if n.kind == "PRUNED" or n.pruned:
            edge_attrs = " [style=dashed, color=red]"
        lines.append(f"  n{n.parent} -> n{n.id}{edge_attrs};")

    lines.append("}")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

def decision_diff_to_dot(minimax_move: int, minimax_val: int, ab_move: int, ab_val: int, out_path: str) -> None:
    """
    Small DOT diagram showing Minimax vs Alpha-Beta decision at the root.
    """
    same = (minimax_move == ab_move) and (minimax_val == ab_val)
    status = "SAME" if same else "DIFFERENT"
    dot = (
        "digraph D {\n"
        "  rankdir=LR;\n"
        "  node [shape=box, fontsize=12];\n"
        f'  root [label="Root\\nDecision: {status}"];\n'
        f'  mm [label="Minimax\\nmove=c{minimax_move}\\nvalue={minimax_val}"];\n'
        f'  ab [label="Alpha-Beta\\nmove=c{ab_move}\\nvalue={ab_val}"];\n'
        "  root -> mm;\n"
        "  root -> ab;\n"
        "}\n"
    )
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(dot)
