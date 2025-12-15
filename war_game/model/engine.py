from collections import deque
from .deck import Deck
from .player import Player


class GameEngine:
    """
    Motorul logic al jocului 'Război'.
    Deocamdată: doar setup (creare jucători, împărțire cărți).
    """

    def __init__(self, war_face_down_count: int = 3) -> None:
        self.war_face_down_count = war_face_down_count
        self.player = Player("You")
        self.cpu = Player("CPU")
        self.pot: list = []  # aici vom pune cărțile din rundă / war
        self.state: str = "idle"

    def reset_game(self) -> None:
        """Creează un deck nou, îl amestecă și împarte cărțile între Player și CPU."""
        deck = Deck()
        deck.shuffle()

        # Curățăm starea veche
        self.player.clear()
        self.cpu.clear()
        self.pot.clear()
        self.state = "idle"

        # Împărțim cărțile alternativ: P, CPU, P, CPU, ...
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
        """Jocul se termină când unul dintre jucători rămâne fără cărți."""
        return not self.player.has_cards() or not self.cpu.has_cards()

    def get_scores(self) -> tuple[int, int]:
        """Întoarce numărul de cărți deținute de Player și CPU."""
        return self.player.card_count(), self.cpu.card_count()
