from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .deck import Deck
from .player import Player
from .card import Card


@dataclass
class RoundResult:
    player_card: Optional[Card]
    cpu_card: Optional[Card]
    winner: Optional[str]  # "player", "cpu", or None
    war_happened: bool
    pot_size: int
    game_over: bool
    message: str


class GameEngine:
    """
    War card game engine (UI-agnostic).

    Rules:
    - Each round: both draw top card; higher value wins pot.
    - Tie: war -> each puts N face-down (as many as possible) + 1 face-up (if possible).
    - If someone cannot place the face-up card during war, they lose the pot.
    - Score = total cards owned (pile size).
    """

    def __init__(self, war_face_down_count: int = 3) -> None:
        self.war_face_down_count = war_face_down_count
        self.player = Player("You")
        self.cpu = Player("CPU")
        self.pot: list[Card] = []
        self.state: str = "idle"

    def reset_game(self) -> None:
        deck = Deck()
        deck.shuffle()

        self.player.clear()
        self.cpu.clear()
        self.pot.clear()
        self.state = "idle"

        toggle = True  # True -> player, False -> cpu
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
        return not self.player.has_cards() or not self.cpu.has_cards()

    def get_scores(self) -> tuple[int, int]:
        return self.player.card_count(), self.cpu.card_count()

    def play_round(self) -> RoundResult:
        """
        Plays one full round (including any chained wars) and awards the pot.
        Returns a RoundResult snapshot useful for UI or testing.
        """
        if self.is_game_over():
            self.state = "game_over"
            return RoundResult(
                player_card=None,
                cpu_card=None,
                winner=None,
                war_happened=False,
                pot_size=0,
                game_over=True,
                message="Game over."
            )

        self.pot.clear()
        self.state = "round"

        p_card = self.player.draw_card()
        c_card = self.cpu.draw_card()

        if p_card is None or c_card is None:
            self.state = "game_over"
            return RoundResult(
                player_card=p_card,
                cpu_card=c_card,
                winner="cpu" if p_card is None else "player",
                war_happened=False,
                pot_size=0,
                game_over=True,
                message="Game over (not enough cards to draw)."
            )

        self.pot.extend([p_card, c_card])

        war_happened = False
        last_p_face = p_card
        last_c_face = c_card

        # Resolve comparisons, including chained wars
        while True:
            if last_p_face.value > last_c_face.value:
                self.player.add_cards_to_bottom(self.pot)
                self.state = "idle"
                return RoundResult(
                    player_card=last_p_face,
                    cpu_card=last_c_face,
                    winner="player",
                    war_happened=war_happened,
                    pot_size=len(self.pot),
                    game_over=self.is_game_over(),
                    message="Player wins the pot."
                )

            if last_p_face.value < last_c_face.value:
                self.cpu.add_cards_to_bottom(self.pot)
                self.state = "idle"
                return RoundResult(
                    player_card=last_p_face,
                    cpu_card=last_c_face,
                    winner="cpu",
                    war_happened=war_happened,
                    pot_size=len(self.pot),
                    game_over=self.is_game_over(),
                    message="CPU wins the pot."
                )

            # Tie -> war
            war_happened = True
            self.state = "war"

            outcome = self._do_war_step()
            # outcome is: ("player"/"cpu"/None, p_face, c_face, game_over, msg)
            winner, p_face, c_face, is_over, msg = outcome
            last_p_face = p_face if p_face is not None else last_p_face
            last_c_face = c_face if c_face is not None else last_c_face

            if winner == "player":
                self.player.add_cards_to_bottom(self.pot)
                self.state = "idle"
                return RoundResult(
                    player_card=last_p_face,
                    cpu_card=last_c_face,
                    winner="player",
                    war_happened=True,
                    pot_size=len(self.pot),
                    game_over=self.is_game_over(),
                    message=msg
                )

            if winner == "cpu":
                self.cpu.add_cards_to_bottom(self.pot)
                self.state = "idle"
                return RoundResult(
                    player_card=last_p_face,
                    cpu_card=last_c_face,
                    winner="cpu",
                    war_happened=True,
                    pot_size=len(self.pot),
                    game_over=self.is_game_over(),
                    message=msg
                )

            # winner None -> could not resolve (both ran out during war)
            self.state = "game_over"
            return RoundResult(
                player_card=last_p_face,
                cpu_card=last_c_face,
                winner=None,
                war_happened=True,
                pot_size=len(self.pot),
                game_over=True,
                message=msg if msg else "Game over during war."
            )

    def _do_war_step(self) -> tuple[Optional[str], Optional[Card], Optional[Card], bool, str]:
        """
        Executes one war step:
        - each puts N face-down (as many as possible)
        - then each puts 1 face-up (if possible)
        Adds all drawn cards to pot.
        Returns: (winner, player_face_up, cpu_face_up, game_over, message)
        """
        # Face-down cards
        p_down = self._draw_up_to(self.player, self.war_face_down_count)
        c_down = self._draw_up_to(self.cpu, self.war_face_down_count)
        self.pot.extend(p_down)
        self.pot.extend(c_down)

        # Face-up card
        p_face = self.player.draw_card()
        c_face = self.cpu.draw_card()

        if p_face is not None:
            self.pot.append(p_face)
        if c_face is not None:
            self.pot.append(c_face)

        # If someone cannot place face-up, they lose the war
        if p_face is None and c_face is None:
            return (None, None, None, True, "Game over: both players ran out of cards during war.")
        if p_face is None:
            return ("cpu", None, c_face, False, "War resolved: player had no face-up card.")
        if c_face is None:
            return ("player", p_face, None, False, "War resolved: CPU had no face-up card.")

        # If both have face-up, compare. If tie again, continue war chain.
        if p_face.value > c_face.value:
            return ("player", p_face, c_face, False, "War resolved: player wins the war pot.")
        if p_face.value < c_face.value:
            return ("cpu", p_face, c_face, False, "War resolved: CPU wins the war pot.")

        # Tie again -> chained war
        return (None, p_face, c_face, False, "War tie: chained war continues.")

    @staticmethod
    def _draw_up_to(player: Player, n: int) -> list[Card]:
        """
        Draw up to n cards (or fewer if player runs out).
        """
        out: list[Card] = []
        for _ in range(n):
            card = player.draw_card()
            if card is None:
                break
            out.append(card)
        return out
