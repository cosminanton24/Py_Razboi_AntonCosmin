import random
from .card import Card, RANKS, SUITS


class Deck:
    def __init__(self) -> None:
        # Creează toate cele 52 de cărți
        self.cards = [Card(rank, suit) for suit in SUITS for rank in RANKS]

    def shuffle(self) -> None:
        """Amestecă pachetul."""
        random.shuffle(self.cards)

    def draw(self) -> Card | None:
        """
        Scoate o carte din vârful pachetului.
        Întoarce None dacă nu mai sunt cărți.
        """
        if self.cards:
            # Considerăm "vârful" ca fiind finalul listei
            return self.cards.pop()
        return None

    def is_empty(self) -> bool:
        return len(self.cards) == 0

    def __len__(self) -> int:
        return len(self.cards)
