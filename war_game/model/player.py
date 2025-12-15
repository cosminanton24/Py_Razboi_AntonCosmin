from collections import deque
from .card import Card


class Player:
    def __init__(self, name: str) -> None:
        self.name = name
        # Coada de cărți ale jucătorului (pile de joc)
        self.pile: deque[Card] = deque()

    def has_cards(self) -> bool:
        """True dacă jucătorul mai are cărți."""
        return len(self.pile) > 0

    def card_count(self) -> int:
        """Numărul de cărți pe care le are jucătorul."""
        return len(self.pile)

    def draw_card(self) -> Card | None:
        """
        Trage o carte din fața cozii (vârful pilonului).
        Întoarce None dacă nu mai sunt cărți.
        """
        if self.pile:
            return self.pile.popleft()
        return None

    def add_cards_to_bottom(self, cards: list[Card]) -> None:
        """Adaugă o listă de cărți la baza pilonului."""
        self.pile.extend(cards)

    def clear(self) -> None:
        """Golește complet pilonul de cărți."""
        self.pile.clear()
