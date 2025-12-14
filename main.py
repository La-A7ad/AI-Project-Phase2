\
from __future__ import annotations
import argparse

from connect4.game import ConnectFour
from connect4.agents import HumanAgent, MinimaxAgent, AlphaBetaAgent
from connect4.visualize import save_snapshot, ensure_dir

def parse_args():
    p = argparse.ArgumentParser(description="Connect Four: Human vs AI (Minimax / Alpha-Beta)")
    p.add_argument("--ai", choices=["minimax", "alphabeta"], default="alphabeta")
    p.add_argument("--depth", type=int, default=5)
    p.add_argument("--trace-depth", type=int, default=3)
    p.add_argument("--snapshots", action="store_true", help="Save board snapshots to outputs/snapshots during play.")
    return p.parse_args()

def main():
    args = parse_args()

    game = ConnectFour()
    human = HumanAgent()

    # Human = Player 1 (X), AI = Player 2 (O)
    ai = MinimaxAgent(ai_player=-1, depth=args.depth, trace_depth=args.trace_depth) if args.ai == "minimax" \
         else AlphaBetaAgent(ai_player=-1, depth=args.depth, trace_depth=args.trace_depth)

    move_index = 0
    if args.snapshots:
        ensure_dir("outputs/snapshots")

    print("You are X (Player 1). AI is O (Player 2).")
    print(game.to_ascii())

    while not game.terminal():
        if game.current_player == 1:
            out = human.select_move(game)
            game.drop_disc(out.move, player=1)
        else:
            out = ai.select_move(game)
            game.drop_disc(out.move, player=-1)
            print(f"\nAI played column {out.move}")
            print(f"AI metrics: time={out.metrics.time_sec:.4f}s, nodes={out.metrics.nodes_expanded}, depth={out.metrics.max_depth_reached}")

        move_index += 1
        print("\n" + game.to_ascii())

        if args.snapshots:
            save_snapshot(game, "outputs/snapshots", move_index, title=f"Move {move_index}")

    w = game.winner()
    if w == 1:
        print("\nResult: You (X) win.")
    elif w == -1:
        print("\nResult: AI (O) wins.")
    else:
        print("\nResult: Draw.")

if __name__ == "__main__":
    main()
