\
from __future__ import annotations
import argparse

from connect4.game import ConnectFour
from connect4.search import minimax_decision, alphabeta_decision, SearchTracer
from connect4.visualize import ensure_dir, tracer_to_dot, tracer_to_json, decision_diff_to_dot, save_snapshot

def parse_args():
    p = argparse.ArgumentParser(description="Phase II artifacts: Minimax vs Alpha-Beta comparison + diagrams")
    p.add_argument("--depth", type=int, default=5, help="Search depth limit")
    p.add_argument("--trace-depth", type=int, default=3, help="How many levels of the tree to trace/export")
    p.add_argument("--position", choices=["empty", "midgame"], default="empty",
                   help="Empty board or a fixed midgame position (for clearer pruning).")
    return p.parse_args()

def setup_midgame(g: ConnectFour):
    # Legal sequence to create a non-trivial position.
    # Columns: 3,3,2,4,2,4,1,5  (X starts)
    seq = [3,3,2,4,2,4,1,5]
    player = 1
    for c in seq:
        g.drop_disc(c, player=player)
        player = -player

def main():
    args = parse_args()
    ensure_dir("outputs")
    ensure_dir("outputs/snapshots")

    g = ConnectFour()
    if args.position == "midgame":
        setup_midgame(g)

    save_snapshot(g, "outputs/snapshots", 0, title=f"Start position ({args.position})")

    # Minimax trace
    mm_tracer = SearchTracer(trace_depth=args.trace_depth)
    mm_move, mm_metrics, mm_tracer = minimax_decision(g, ai_player=g.current_player, depth_limit=args.depth, tracer=mm_tracer)

    # Alpha-Beta trace
    ab_tracer = SearchTracer(trace_depth=args.trace_depth)
    ab_move, ab_metrics, ab_tracer = alphabeta_decision(g, ai_player=g.current_player, depth_limit=args.depth, tracer=ab_tracer)

    # Export partial trees
    tracer_to_json(mm_tracer, "outputs/tree_minimax.json")
    tracer_to_json(ab_tracer, "outputs/tree_alphabeta.json")
    tracer_to_dot(mm_tracer, "outputs/tree_minimax.dot", title=f"Minimax (depth={args.depth}, trace_depth={args.trace_depth})")
    tracer_to_dot(ab_tracer, "outputs/tree_alphabeta.dot", title=f"Alpha-Beta (depth={args.depth}, trace_depth={args.trace_depth})")

    # Decision difference diagram
    mm_root_val = mm_tracer.nodes[0].value if mm_tracer.nodes and mm_tracer.nodes[0].value is not None else 0
    ab_root_val = ab_tracer.nodes[0].value if ab_tracer.nodes and ab_tracer.nodes[0].value is not None else 0
    decision_diff_to_dot(mm_move, int(mm_root_val), ab_move, int(ab_root_val), "outputs/decision_diff.dot")

    # Performance comparison summary
    summary = f"""\
Performance Comparison (same position, same depth limit)

Position: {args.position}
Depth limit: {args.depth}

Minimax:
  time_sec          = {mm_metrics.time_sec:.6f}
  nodes_expanded    = {mm_metrics.nodes_expanded}
  max_depth_reached = {mm_metrics.max_depth_reached}
  nodes_per_sec     = {mm_metrics.nodes_per_sec:.2f}
  chosen_move       = {mm_move}

Alpha-Beta:
  time_sec          = {ab_metrics.time_sec:.6f}
  nodes_expanded    = {ab_metrics.nodes_expanded}
  max_depth_reached = {ab_metrics.max_depth_reached}
  nodes_per_sec     = {ab_metrics.nodes_per_sec:.2f}
  chosen_move       = {ab_move}

Decision comparison:
  same_move?        = {mm_move == ab_move}
  same_root_value?  = {mm_root_val == ab_root_val}
"""
    with open("outputs/performance_comparison.txt", "w", encoding="utf-8") as f:
        f.write(summary)

    print(summary)
    print("Wrote outputs to ./outputs")

if __name__ == "__main__":
    main()
