\
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional, Tuple
import time

from .game import ConnectFour
from .evaluation import evaluate, WIN_SCORE

@dataclass
class SearchMetrics:
    time_sec: float = 0.0
    nodes_expanded: int = 0
    max_depth_reached: int = 0

    @property
    def nodes_per_sec(self) -> float:
        return self.nodes_expanded / self.time_sec if self.time_sec > 0 else float("inf")

@dataclass
class TraceNode:
    id: int
    parent: Optional[int]
    move: Optional[int]      # column index (None for root)
    depth: int
    turn_player: int         # whose turn at this node (+1 / -1)
    kind: str                # "MAX", "MIN", or "PRUNED"
    alpha: Optional[int] = None
    beta: Optional[int] = None
    value: Optional[int] = None
    pruned: bool = False

class SearchTracer:
    """
    Collect a PARTIAL search tree trace (up to trace_depth).
    For Alpha-Beta, pruned siblings are recorded as pseudo nodes.
    """
    def __init__(self, trace_depth: int = 3):
        self.trace_depth = trace_depth
        self.nodes: List[TraceNode] = []
        self._next_id = 0

    def new_node(self, parent: Optional[int], move: Optional[int], depth: int,
                 turn_player: int, kind: str, alpha: Optional[int]=None, beta: Optional[int]=None,
                 pruned: bool=False) -> int:
        node_id = self._next_id
        self._next_id += 1
        self.nodes.append(TraceNode(
            id=node_id, parent=parent, move=move, depth=depth,
            turn_player=turn_player, kind=kind, alpha=alpha, beta=beta, pruned=pruned
        ))
        return node_id

    def set_value(self, node_id: int, value: int, alpha: Optional[int]=None, beta: Optional[int]=None) -> None:
        for n in self.nodes:
            if n.id == node_id:
                n.value = value
                if alpha is not None:
                    n.alpha = alpha
                if beta is not None:
                    n.beta = beta
                return

def minimax_decision(game: ConnectFour, ai_player: int, depth_limit: int,
                     tracer: Optional[SearchTracer] = None) -> Tuple[int, SearchMetrics, Optional[SearchTracer]]:
    metrics = SearchMetrics()
    t0 = time.perf_counter()

    root_id = None
    if tracer is not None:
        root_kind = "MAX" if game.current_player == ai_player else "MIN"
        root_id = tracer.new_node(None, None, 0, game.current_player, root_kind)

    def terminal_value() -> int:
        w = game.winner()
        if w == ai_player:
            return WIN_SCORE
        if w == -ai_player:
            return -WIN_SCORE
        return 0

    def max_value(d: int, node_id: Optional[int]) -> int:
        metrics.nodes_expanded += 1
        metrics.max_depth_reached = max(metrics.max_depth_reached, d)

        if game.terminal():
            return terminal_value()
        if d >= depth_limit:
            return evaluate(game, ai_player)

        v = -10**18
        for a in game.actions():
            mv = game.drop_disc(a)
            child_id = None
            if tracer is not None and d < tracer.trace_depth:
                kind = "MAX" if game.current_player == ai_player else "MIN"
                child_id = tracer.new_node(node_id, a, d+1, game.current_player, kind)
            val = min_value(d+1, child_id)
            game.undo_disc(mv)
            if val > v:
                v = val
        if tracer is not None and node_id is not None and d <= tracer.trace_depth:
            tracer.set_value(node_id, v)
        return v

    def min_value(d: int, node_id: Optional[int]) -> int:
        metrics.nodes_expanded += 1
        metrics.max_depth_reached = max(metrics.max_depth_reached, d)

        if game.terminal():
            return terminal_value()
        if d >= depth_limit:
            return evaluate(game, ai_player)

        v = 10**18
        for a in game.actions():
            mv = game.drop_disc(a)
            child_id = None
            if tracer is not None and d < tracer.trace_depth:
                kind = "MAX" if game.current_player == ai_player else "MIN"
                child_id = tracer.new_node(node_id, a, d+1, game.current_player, kind)
            val = max_value(d+1, child_id)
            game.undo_disc(mv)
            if val < v:
                v = val
        if tracer is not None and node_id is not None and d <= tracer.trace_depth:
            tracer.set_value(node_id, v)
        return v

    best_move = None
    if game.current_player == ai_player:
        best_val = -10**18
        for a in game.actions():
            mv = game.drop_disc(a)
            child_id = None
            if tracer is not None and tracer.trace_depth >= 1:
                kind = "MAX" if game.current_player == ai_player else "MIN"
                child_id = tracer.new_node(root_id, a, 1, game.current_player, kind)
            val = min_value(1, child_id)
            game.undo_disc(mv)
            if val > best_val:
                best_val = val
                best_move = a
        if tracer is not None and root_id is not None:
            tracer.set_value(root_id, best_val)
    else:
        # Not expected in normal use, but handled.
        best_val = 10**18
        for a in game.actions():
            mv = game.drop_disc(a)
            child_id = None
            if tracer is not None and tracer.trace_depth >= 1:
                kind = "MAX" if game.current_player == ai_player else "MIN"
                child_id = tracer.new_node(root_id, a, 1, game.current_player, kind)
            val = max_value(1, child_id)
            game.undo_disc(mv)
            if val < best_val:
                best_val = val
                best_move = a
        if tracer is not None and root_id is not None:
            tracer.set_value(root_id, best_val)

    metrics.time_sec = time.perf_counter() - t0
    return int(best_move), metrics, tracer

def alphabeta_decision(game: ConnectFour, ai_player: int, depth_limit: int,
                       tracer: Optional[SearchTracer] = None) -> Tuple[int, SearchMetrics, Optional[SearchTracer]]:
    metrics = SearchMetrics()
    t0 = time.perf_counter()

    INF = 10**18
    root_id = None
    if tracer is not None:
        root_kind = "MAX" if game.current_player == ai_player else "MIN"
        root_id = tracer.new_node(None, None, 0, game.current_player, root_kind, alpha=-INF, beta=INF)

    def terminal_value() -> int:
        w = game.winner()
        if w == ai_player:
            return WIN_SCORE
        if w == -ai_player:
            return -WIN_SCORE
        return 0

    def max_value(d: int, alpha: int, beta: int, node_id: Optional[int]) -> int:
        metrics.nodes_expanded += 1
        metrics.max_depth_reached = max(metrics.max_depth_reached, d)

        if game.terminal():
            return terminal_value()
        if d >= depth_limit:
            return evaluate(game, ai_player)

        v = -INF
        acts = game.actions()
        for i, a in enumerate(acts):
            mv = game.drop_disc(a)
            child_id = None
            if tracer is not None and d < tracer.trace_depth:
                kind = "MAX" if game.current_player == ai_player else "MIN"
                child_id = tracer.new_node(node_id, a, d+1, game.current_player, kind, alpha=alpha, beta=beta)
            val = min_value(d+1, alpha, beta, child_id)
            game.undo_disc(mv)

            if val > v:
                v = val
            if v > alpha:
                alpha = v

            if alpha >= beta:
                if tracer is not None and d < tracer.trace_depth:
                    for pruned_a in acts[i+1:]:
                        tracer.new_node(node_id, pruned_a, d+1, game.current_player, "PRUNED",
                                        alpha=alpha, beta=beta, pruned=True)
                break

        if tracer is not None and node_id is not None and d <= tracer.trace_depth:
            tracer.set_value(node_id, v, alpha=alpha, beta=beta)
        return v

    def min_value(d: int, alpha: int, beta: int, node_id: Optional[int]) -> int:
        metrics.nodes_expanded += 1
        metrics.max_depth_reached = max(metrics.max_depth_reached, d)

        if game.terminal():
            return terminal_value()
        if d >= depth_limit:
            return evaluate(game, ai_player)

        v = INF
        acts = game.actions()
        for i, a in enumerate(acts):
            mv = game.drop_disc(a)
            child_id = None
            if tracer is not None and d < tracer.trace_depth:
                kind = "MAX" if game.current_player == ai_player else "MIN"
                child_id = tracer.new_node(node_id, a, d+1, game.current_player, kind, alpha=alpha, beta=beta)
            val = max_value(d+1, alpha, beta, child_id)
            game.undo_disc(mv)

            if val < v:
                v = val
            if v < beta:
                beta = v

            if alpha >= beta:
                if tracer is not None and d < tracer.trace_depth:
                    for pruned_a in acts[i+1:]:
                        tracer.new_node(node_id, pruned_a, d+1, game.current_player, "PRUNED",
                                        alpha=alpha, beta=beta, pruned=True)
                break

        if tracer is not None and node_id is not None and d <= tracer.trace_depth:
            tracer.set_value(node_id, v, alpha=alpha, beta=beta)
        return v

    best_move = None
    alpha, beta = -INF, INF

    if game.current_player == ai_player:
        best_val = -INF
        acts = game.actions()
        for i, a in enumerate(acts):
            mv = game.drop_disc(a)
            child_id = None
            if tracer is not None and tracer.trace_depth >= 1:
                kind = "MAX" if game.current_player == ai_player else "MIN"
                child_id = tracer.new_node(root_id, a, 1, game.current_player, kind, alpha=alpha, beta=beta)
            val = min_value(1, alpha, beta, child_id)
            game.undo_disc(mv)

            if val > best_val:
                best_val = val
                best_move = a
            if best_val > alpha:
                alpha = best_val

            if alpha >= beta:
                if tracer is not None and tracer.trace_depth >= 1:
                    for pruned_a in acts[i+1:]:
                        tracer.new_node(root_id, pruned_a, 1, game.current_player, "PRUNED",
                                        alpha=alpha, beta=beta, pruned=True)
                break

        if tracer is not None and root_id is not None:
            tracer.set_value(root_id, best_val, alpha=alpha, beta=beta)
    else:
        # Not expected in normal use, but handled.
        best_val = INF
        acts = game.actions()
        for i, a in enumerate(acts):
            mv = game.drop_disc(a)
            child_id = None
            if tracer is not None and tracer.trace_depth >= 1:
                kind = "MAX" if game.current_player == ai_player else "MIN"
                child_id = tracer.new_node(root_id, a, 1, game.current_player, kind, alpha=alpha, beta=beta)
            val = max_value(1, alpha, beta, child_id)
            game.undo_disc(mv)

            if val < best_val:
                best_val = val
                best_move = a
            if best_val < beta:
                beta = best_val

            if alpha >= beta:
                if tracer is not None and tracer.trace_depth >= 1:
                    for pruned_a in acts[i+1:]:
                        tracer.new_node(root_id, pruned_a, 1, game.current_player, "PRUNED",
                                        alpha=alpha, beta=beta, pruned=True)
                break

        if tracer is not None and root_id is not None:
            tracer.set_value(root_id, best_val, alpha=alpha, beta=beta)

    metrics.time_sec = time.perf_counter() - t0
    return int(best_move), metrics, tracer
