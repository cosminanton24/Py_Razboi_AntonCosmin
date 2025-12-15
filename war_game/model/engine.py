from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .card import Card
from .deck import Deck
from .player import Player


@dataclass
class StepResult:
    action: str  # "draw", "compare", "war_start", "war_down", "war_up", "award", "game_over"
    player_card: Optional[Card]
    cpu_card: Optional[Card]
    player_down_count: int
    cpu_down_count: int
    pot_size: int
    round_over: bool
    game_over: bool
    winner: Optional[str]  # "player", "cpu", or None
    message: str


class GameEngine:
    """
    Step-based War engine for UI visualization.

    Flow:
    - next_step() drives the round in multiple UI-visible steps:
      draw -> compare -> (if tie) war_start -> war_down -> war_up -> compare -> ...
      -> award pot -> round_over -> idle

    War:
    - Each tie triggers war:
      N face-down (as many as possible) then 1 face-up (if possible).
    - If someone cannot place the face-up card during war, they lose the pot.
    - Chained wars are handled by looping back to war_start.
    """

    def __init__(self, war_face_down_count: int = 3) -> None:
        self.war_face_down_count = war_face_down_count
        self.player = Player("You")
        self.cpu = Player("CPU")

        self.pot: list[Card] = []
        self.state: str = "idle"  # "idle", "compare", "war_down", "war_up", "game_over"

        self.last_player_face: Optional[Card] = None
        self.last_cpu_face: Optional[Card] = None

    def reset_game(self) -> None:
        deck = Deck()
        deck.shuffle()

        self.player.clear()
        self.cpu.clear()
        self.pot.clear()
        self.state = "idle"
        self.last_player_face = None
        self.last_cpu_face = None

        toggle = True
        while not deck.is_empty():
            card = deck.draw()
            if card is None:
                break
            if toggle:
                self.player.pile.append(card)
            else:
                self.cpu.pile.append(card)
            toggle = not toggle

    def is_game_over(self) -> bool:
        return (not self.player.has_cards()) or (not self.cpu.has_cards())

    def get_scores(self) -> tuple[int, int]:
        return self.player.card_count(), self.cpu.card_count()

    def in_round(self) -> bool:
        return self.state != "idle" and self.state != "game_over"

    def next_step(self) -> StepResult:
        """
        Advances the game by one visual step.
        Call repeatedly from UI (Play/Next) to visualize wars.
        """
        if self.state == "game_over" or self.is_game_over():
            self.state = "game_over"
            return StepResult(
                action="game_over",
                player_card=self.last_player_face,
                cpu_card=self.last_cpu_face,
                player_down_count=0,
                cpu_down_count=0,
                pot_size=len(self.pot),
                round_over=True,
                game_over=True,
                winner=self._who_wins_game(),
                message="Game over."
            )

        if self.state == "idle":
            return self._start_round_draw()

        if self.state == "compare":
            return self._step_compare()

        if self.state == "war_down":
            return self._step_war_down()

        if self.state == "war_up":
            return self._step_war_up()

        # Fallback
        self.state = "game_over"
        return StepResult(
            action="game_over",
            player_card=self.last_player_face,
            cpu_card=self.last_cpu_face,
            player_down_count=0,
            cpu_down_count=0,
            pot_size=len(self.pot),
            round_over=True,
            game_over=True,
            winner=self._who_wins_game(),
            message="Game over (invalid state)."
        )

    def _start_round_draw(self) -> StepResult:
        self.pot.clear()

        p = self.player.draw_card()
        c = self.cpu.draw_card()

        # If someone cannot draw, game ends
        if p is None or c is None:
            self.last_player_face = p
            self.last_cpu_face = c
            self.state = "game_over"
            return StepResult(
                action="game_over",
                player_card=p,
                cpu_card=c,
                player_down_count=0,
                cpu_down_count=0,
                pot_size=len(self.pot),
                round_over=True,
                game_over=True,
                winner="cpu" if p is None else "player",
                message="Game over (not enough cards to draw)."
            )

        self.last_player_face = p
        self.last_cpu_face = c
        self.pot.extend([p, c])
        self.state = "compare"

        return StepResult(
            action="draw",
            player_card=p,
            cpu_card=c,
            player_down_count=0,
            cpu_down_count=0,
            pot_size=len(self.pot),
            round_over=False,
            game_over=False,
            winner=None,
            message="Draw."
        )

    def _step_compare(self) -> StepResult:
        p = self.last_player_face
        c = self.last_cpu_face

        if p is None or c is None:
            self.state = "game_over"
            return StepResult(
                action="game_over",
                player_card=p,
                cpu_card=c,
                player_down_count=0,
                cpu_down_count=0,
                pot_size=len(self.pot),
                round_over=True,
                game_over=True,
                winner=self._who_wins_game(),
                message="Game over."
            )

        if p.value > c.value:
            self.player.add_cards_to_bottom(self.pot)
            msg = "Player wins the pot."
            winner = "player"
            self.state = "idle"
            return StepResult(
                action="award",
                player_card=p,
                cpu_card=c,
                player_down_count=0,
                cpu_down_count=0,
                pot_size=len(self.pot),
                round_over=True,
                game_over=self.is_game_over(),
                winner=winner,
                message=msg
            )

        if p.value < c.value:
            self.cpu.add_cards_to_bottom(self.pot)
            msg = "CPU wins the pot."
            winner = "cpu"
            self.state = "idle"
            return StepResult(
                action="award",
                player_card=p,
                cpu_card=c,
                player_down_count=0,
                cpu_down_count=0,
                pot_size=len(self.pot),
                round_over=True,
                game_over=self.is_game_over(),
                winner=winner,
                message=msg
            )

        # Tie -> war sequence begins
        self.state = "war_down"
        return StepResult(
            action="war_start",
            player_card=p,
            cpu_card=c,
            player_down_count=0,
            cpu_down_count=0,
            pot_size=len(self.pot),
            round_over=False,
            game_over=False,
            winner=None,
            message="War!"
        )

    def _step_war_down(self) -> StepResult:
        # Each puts N face-down (as many as possible)
        p_down = self._draw_up_to(self.player, self.war_face_down_count)
        c_down = self._draw_up_to(self.cpu, self.war_face_down_count)

        self.pot.extend(p_down)
        self.pot.extend(c_down)

        self.state = "war_up"
        return StepResult(
            action="war_down",
            player_card=self.last_player_face,
            cpu_card=self.last_cpu_face,
            player_down_count=len(p_down),
            cpu_down_count=len(c_down),
            pot_size=len(self.pot),
            round_over=False,
            game_over=False,
            winner=None,
            message="War: face-down cards placed."
        )

    def _step_war_up(self) -> StepResult:
        # Each puts 1 face-up (if possible)
        p_face = self.player.draw_card()
        c_face = self.cpu.draw_card()

        if p_face is not None:
            self.pot.append(p_face)
        if c_face is not None:
            self.pot.append(c_face)

        self.last_player_face = p_face if p_face is not None else self.last_player_face
        self.last_cpu_face = c_face if c_face is not None else self.last_cpu_face

        # If someone cannot place face-up, they lose the pot immediately
        if p_face is None and c_face is None:
            self.state = "game_over"
            return StepResult(
                action="game_over",
                player_card=self.last_player_face,
                cpu_card=self.last_cpu_face,
                player_down_count=0,
                cpu_down_count=0,
                pot_size=len(self.pot),
                round_over=True,
                game_over=True,
                winner=None,
                message="Game over: both ran out of cards during war."
            )

        if p_face is None:
            self.cpu.add_cards_to_bottom(self.pot)
            self.state = "idle"
            return StepResult(
                action="award",
                player_card=self.last_player_face,
                cpu_card=self.last_cpu_face,
                player_down_count=0,
                cpu_down_count=0,
                pot_size=len(self.pot),
                round_over=True,
                game_over=self.is_game_over(),
                winner="cpu",
                message="War resolved: player had no face-up card. CPU wins pot."
            )

        if c_face is None:
            self.player.add_cards_to_bottom(self.pot)
            self.state = "idle"
            return StepResult(
                action="award",
                player_card=self.last_player_face,
                cpu_card=self.last_cpu_face,
                player_down_count=0,
                cpu_down_count=0,
                pot_size=len(self.pot),
                round_over=True,
                game_over=self.is_game_over(),
                winner="player",
                message="War resolved: CPU had no face-up card. Player wins pot."
            )

        # Both have face-up -> show reveal now, compare next step
        self.state = "compare"
        return StepResult(
            action="war_up",
            player_card=p_face,
            cpu_card=c_face,
            player_down_count=0,
            cpu_down_count=0,
            pot_size=len(self.pot),
            round_over=False,
            game_over=False,
            winner=None,
            message="War: face-up reveal."
        )

    @staticmethod
    def _draw_up_to(player: Player, n: int) -> list[Card]:
        out: list[Card] = []
        for _ in range(n):
            card = player.draw_card()
            if card is None:
                break
            out.append(card)
        return out

    def _who_wins_game(self) -> Optional[str]:
        if self.player.has_cards() and not self.cpu.has_cards():
            return "player"
        if self.cpu.has_cards() and not self.player.has_cards():
            return "cpu"
        return None
