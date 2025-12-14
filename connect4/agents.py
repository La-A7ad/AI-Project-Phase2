\
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

from .game import ConnectFour
from .search import minimax_decision, alphabeta_decision, SearchMetrics, SearchTracer

@dataclass
class AgentOutput:
    move: int
    metrics: SearchMetrics
    tracer: Optional[SearchTracer] = None

class BaseAgent:
    def select_move(self, game: ConnectFour) -> AgentOutput:
        raise NotImplementedError

class HumanAgent(BaseAgent):
    def select_move(self, game: ConnectFour) -> AgentOutput:
        while True:
            raw = input(f"Choose column {game.actions()} : ").strip()
            try:
                col = int(raw)
            except ValueError:
                print("Enter an integer column index.")
                continue
            if col not in game.actions():
                print("Invalid move. Try again.")
                continue
            return AgentOutput(move=col, metrics=SearchMetrics())

class MinimaxAgent(BaseAgent):
    def __init__(self, ai_player: int, depth: int = 5, trace_depth: int = 3, enable_trace: bool = False):
        self.ai_player = ai_player
        self.depth = depth
        self.trace_depth = trace_depth
        self.enable_trace = enable_trace

    def select_move(self, game: ConnectFour) -> AgentOutput:
        tracer = SearchTracer(self.trace_depth) if self.enable_trace else None
        move, metrics, tracer = minimax_decision(game, self.ai_player, self.depth, tracer)
        return AgentOutput(move=move, metrics=metrics, tracer=tracer)

class AlphaBetaAgent(BaseAgent):
    def __init__(self, ai_player: int, depth: int = 5, trace_depth: int = 3, enable_trace: bool = False):
        self.ai_player = ai_player
        self.depth = depth
        self.trace_depth = trace_depth
        self.enable_trace = enable_trace

    def select_move(self, game: ConnectFour) -> AgentOutput:
        tracer = SearchTracer(self.trace_depth) if self.enable_trace else None
        move, metrics, tracer = alphabeta_decision(game, self.ai_player, self.depth, tracer)
        return AgentOutput(move=move, metrics=metrics, tracer=tracer)
