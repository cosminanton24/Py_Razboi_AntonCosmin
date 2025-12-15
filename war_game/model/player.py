from collections import deque
from .card import Card


class Player:
    def __init__(self, name: str) -> None:
        self.name = name
        self.pile: deque[Card] = deque()

    def has_cards(self) -> bool:
        """true if player has cards left."""
        return len(self.pile) > 0

    def card_count(self) -> int:
        """number of cards of player"""
        return len(self.pile)

    def draw_card(self) -> Card | None:
        """
        draw a card from the front of the queue (top of the pile).
        Returns None if no cards left.
        """
        if self.pile:
            return self.pile.popleft()
        return None

    def add_cards_to_bottom(self, cards: list[Card]) -> None:
        """Adds a list of cards to the bottom of the pile."""
        self.pile.extend(cards)

    def clear(self) -> None:
        """empties the player's pile."""
        self.pile.clear()
