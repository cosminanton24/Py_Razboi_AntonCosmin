from collections import deque
from .card import Card


class Player:
    def __init__(self, name: str) -> None:
        self.name = name
        self.pile: deque[Card] = deque()

    def has_cards(self) -> bool:
        return len(self.pile) > 0

    def card_count(self) -> int:
        return len(self.pile)

    def draw_card(self) -> Card | None:
        if self.pile:
            return self.pile.popleft()
        return None

    def add_cards_to_bottom(self, cards: list[Card]) -> None:
        self.pile.extend(cards)

    def clear(self) -> None:
        self.pile.clear()
