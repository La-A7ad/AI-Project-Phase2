\
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional, Tuple

# Board coordinates:
# - board[row][col]
# - row 0 is the TOP, row (rows-1) is the BOTTOM.
#
# Players are encoded as:
#   +1  => Player 1 (X)
#   -1  => Player 2 (O)
# Empty cell is 0.

@dataclass
class MoveResult:
    row: int
    col: int
    player: int

class ConnectFour:
    def __init__(self, rows: int = 6, cols: int = 7, connect: int = 4):
        if rows <= 0 or cols <= 0:
            raise ValueError("rows and cols must be positive.")
        if connect < 3:
            raise ValueError("connect should be >= 3.")
        self.rows = rows
        self.cols = cols
        self.connect = connect
        self.board: List[List[int]] = [[0 for _ in range(cols)] for _ in range(rows)]
        self.current_player: int = 1  # Player 1 starts by default
        self.last_move: Optional[MoveResult] = None

    def reset(self) -> None:
        for r in range(self.rows):
            for c in range(self.cols):
                self.board[r][c] = 0
        self.current_player = 1
        self.last_move = None

    def copy(self) -> "ConnectFour":
        g = ConnectFour(self.rows, self.cols, self.connect)
        g.current_player = self.current_player
        g.last_move = self.last_move
        g.board = [row[:] for row in self.board]
        return g

    def actions(self) -> List[int]:
        """Valid actions are all columns that are not full."""
        return [c for c in range(self.cols) if self.board[0][c] == 0]

    def is_full(self) -> bool:
        return all(self.board[0][c] != 0 for c in range(self.cols))

    def drop_disc(self, col: int, player: Optional[int] = None) -> MoveResult:
        """Apply a move in-place. Returns the (row,col,player) where the disc landed."""
        if player is None:
            player = self.current_player
        if not (0 <= col < self.cols):
            raise ValueError("Column out of bounds.")
        if self.board[0][col] != 0:
            raise ValueError("Column is full.")

        for r in range(self.rows - 1, -1, -1):
            if self.board[r][col] == 0:
                self.board[r][col] = player
                mv = MoveResult(row=r, col=col, player=player)
                self.last_move = mv
                if player == self.current_player:
                    self.current_player = -self.current_player
                return mv

        raise RuntimeError("Failed to drop disc.")

    def undo_disc(self, move: MoveResult) -> None:
        """Undo a previously applied move."""
        r, c, p = move.row, move.col, move.player
        if self.board[r][c] != p:
            raise ValueError("Undo mismatch: board cell does not match the move.")
        self.board[r][c] = 0
        self.last_move = None
        self.current_player = p

    def winner(self) -> int:
        """Return +1 if Player 1 wins, -1 if Player 2 wins, else 0."""
        if self.last_move is None:
            return 0
        r, c, p = self.last_move.row, self.last_move.col, self.last_move.player
        return p if self._is_winning_move(r, c, p) else 0

    def terminal(self) -> bool:
        return self.winner() != 0 or self.is_full()

    def _is_winning_move(self, r: int, c: int, p: int) -> bool:
        directions = [(0, 1), (1, 0), (1, 1), (-1, 1)]
        for dr, dc in directions:
            count = 1
            count += self._count_dir(r, c, p, dr, dc)
            count += self._count_dir(r, c, p, -dr, -dc)
            if count >= self.connect:
                return True
        return False

    def _count_dir(self, r: int, c: int, p: int, dr: int, dc: int) -> int:
        cnt = 0
        rr, cc = r + dr, c + dc
        while 0 <= rr < self.rows and 0 <= cc < self.cols and self.board[rr][cc] == p:
            cnt += 1
            rr += dr
            cc += dc
        return cnt

    def serialize(self) -> Tuple[Tuple[int, ...], int]:
        flat = []
        for r in range(self.rows):
            flat.extend(self.board[r])
        return (tuple(flat), self.current_player)

    def to_ascii(self) -> str:
        def cell(v: int) -> str:
            if v == 1:
                return "X"
            if v == -1:
                return "O"
            return "."
        lines = ["  " + " ".join(str(i) for i in range(self.cols))]
        for r in range(self.rows):
            lines.append(str(r) + " " + " ".join(cell(self.board[r][c]) for c in range(self.cols)))
        return "\n".join(lines)

    def pretty_last_move(self) -> str:
        if self.last_move is None:
            return "None"
        p = "X" if self.last_move.player == 1 else "O"
        return f"{p} @ (row={self.last_move.row}, col={self.last_move.col})"
