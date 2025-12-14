\
from __future__ import annotations
from typing import List
from .game import ConnectFour

WIN_SCORE = 10**9  # terminal win/loss magnitude

def evaluate(game: ConnectFour, player: int) -> int:
    """
    Heuristic evaluation from the perspective of `player` (+1 or -1).
    Positive => good for `player`.
    """
    w = game.winner()
    if w == player:
        return WIN_SCORE
    if w == -player:
        return -WIN_SCORE
    if game.is_full():
        return 0

    board = game.board
    rows, cols = game.rows, game.cols
    score = 0

    # Center column preference
    center_col = cols // 2
    center_delta = 0
    for r in range(rows):
        if board[r][center_col] == player:
            center_delta += 1
        elif board[r][center_col] == -player:
            center_delta -= 1
    score += 6 * center_delta

    def score_window(window: List[int]) -> int:
        p_count = window.count(player)
        o_count = window.count(-player)
        e_count = window.count(0)

        # Blocked window (contains both)
        if p_count > 0 and o_count > 0:
            return 0

        if p_count == 4:
            return 100000
        if p_count == 3 and e_count == 1:
            return 200
        if p_count == 2 and e_count == 2:
            return 30

        if o_count == 4:
            return -100000
        if o_count == 3 and e_count == 1:
            return -220
        if o_count == 2 and e_count == 2:
            return -35

        return 0

    # Horizontal
    for r in range(rows):
        for c in range(cols - 3):
            score += score_window([board[r][c+i] for i in range(4)])

    # Vertical
    for c in range(cols):
        for r in range(rows - 3):
            score += score_window([board[r+i][c] for i in range(4)])

    # Diagonal down-right
    for r in range(rows - 3):
        for c in range(cols - 3):
            score += score_window([board[r+i][c+i] for i in range(4)])

    # Diagonal up-right
    for r in range(3, rows):
        for c in range(cols - 3):
            score += score_window([board[r-i][c+i] for i in range(4)])

    return score
