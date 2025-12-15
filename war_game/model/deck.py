import random
from .card import Card, RANKS, SUITS


class Deck:
    def __init__(self) -> None:
        #creates a standard 52-card deck
        self.cards = [Card(rank, suit) for suit in SUITS for rank in RANKS]

    def shuffle(self) -> None:
        """Shuffles the deck."""
        random.shuffle(self.cards)

    def draw(self) -> Card | None:
        """
        Draws a card from the top of the deck.
        Returns None if no cards left.
        """
        if self.cards:
            # Consider the "top" as the end of the list
            return self.cards.pop()
        return None

    def is_empty(self) -> bool:
        return len(self.cards) == 0

    def __len__(self) -> int:
        return len(self.cards)
