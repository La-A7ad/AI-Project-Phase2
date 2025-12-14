from __future__ import annotations
import argparse
import tkinter as tk

from connect4.game import ConnectFour
from connect4.agents import MinimaxAgent, AlphaBetaAgent


def parse_args():
    p = argparse.ArgumentParser(description="Connect Four GUI (Tkinter) - Human vs AI")
    p.add_argument("--ai", choices=["minimax", "alphabeta"], default="alphabeta")
    p.add_argument("--depth", type=int, default=5)
    return p.parse_args()


class ConnectFourGUI:
    def __init__(self, ai_kind: str, depth: int):
        self.game = ConnectFour()
        self.human_player = 1   # X
        self.ai_player = -1     # O

        if ai_kind == "minimax":
            self.ai = MinimaxAgent(ai_player=self.ai_player, depth=depth, enable_trace=False)
        else:
            self.ai = AlphaBetaAgent(ai_player=self.ai_player, depth=depth, enable_trace=False)

        # --- GUI config (minimal) ---
        self.cell = 80
        self.pad = 10
        self.cols = self.game.cols
        self.rows = self.game.rows

        w = self.pad * 2 + self.cols * self.cell
        h = self.pad * 2 + self.rows * self.cell + 50  # extra space for status

        self.root = tk.Tk()
        self.root.title("Connect Four - Human (X) vs AI (O)")

        self.canvas = tk.Canvas(self.root, width=w, height=h, highlightthickness=0)
        self.canvas.pack()

        self.status = tk.Label(self.root, text="", anchor="w")
        self.status.pack(fill="x")

        # Pre-create circle items (so updates are fast)
        self.discs = [[None for _ in range(self.cols)] for _ in range(self.rows)]
        self._draw_board()

        self.canvas.bind("<Button-1>", self.on_click)

        self.update_status("Your turn: click a column (X).")
        self.refresh_board()

    def _draw_board(self):
        # Background
        w = self.pad * 2 + self.cols * self.cell
        h = self.pad * 2 + self.rows * self.cell
        self.canvas.create_rectangle(0, 0, w, h, outline="", fill="#1E4EA1")  # simple blue board

        # Column numbers
        for c in range(self.cols):
            x = self.pad + c * self.cell + self.cell // 2
            self.canvas.create_text(x, 5, text=str(c), fill="white", anchor="n", font=("Arial", 14, "bold"))

        # Holes/discs
        for r in range(self.rows):
            for c in range(self.cols):
                x0 = self.pad + c * self.cell + 10
                y0 = self.pad + r * self.cell + 25
                x1 = self.pad + (c + 1) * self.cell - 10
                y1 = self.pad + (r + 1) * self.cell + 5

                # Default empty hole
                oid = self.canvas.create_oval(x0, y0, x1, y1, outline="", fill="white")
                self.discs[r][c] = oid

    def refresh_board(self):
        # Map board values to colors
        for r in range(self.rows):
            for c in range(self.cols):
                v = self.game.board[r][c]
                if v == 1:
                    color = "red"     # X
                elif v == -1:
                    color = "yellow"  # O
                else:
                    color = "white"
                self.canvas.itemconfig(self.discs[r][c], fill=color)

    def update_status(self, msg: str):
        self.status.config(text=msg)

    def on_click(self, event):
        if self.game.terminal():
            return
        if self.game.current_player != self.human_player:
            return

        # Convert click x -> column
        x = event.x - self.pad
        col = x // self.cell
        if col < 0 or col >= self.cols:
            return
        col = int(col)

        if col not in self.game.actions():
            self.update_status("That column is full. Choose another.")
            return

        # Human move
        self.game.drop_disc(col, player=self.human_player)
        self.refresh_board()

        if self.game.terminal():
            self.finish_game()
            return

        # AI move (small delay so UI updates first)
        self.update_status("AI thinking...")
        self.root.after(80, self.ai_turn)

    def ai_turn(self):
        if self.game.terminal():
            return
        if self.game.current_player != self.ai_player:
            return

        out = self.ai.select_move(self.game)
        self.game.drop_disc(out.move, player=self.ai_player)
        self.refresh_board()

        if self.game.terminal():
            self.finish_game()
            return

        self.update_status(
            f"Your turn (X). AI played col {out.move}. "
            f"(t={out.metrics.time_sec:.4f}s, nodes={out.metrics.nodes_expanded}, depth={out.metrics.max_depth_reached})"
        )

    def finish_game(self):
        w = self.game.winner()
        if w == 1:
            self.update_status("Game over: You win (X).")
        elif w == -1:
            self.update_status("Game over: AI wins (O).")
        else:
            self.update_status("Game over: Draw.")

    def run(self):
        self.root.mainloop()


def main():
    args = parse_args()
    app = ConnectFourGUI(ai_kind=args.ai, depth=args.depth)
    app.run()


if __name__ == "__main__":
    main()
