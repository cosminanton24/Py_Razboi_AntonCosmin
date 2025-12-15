from dataclasses import dataclass


RANKS = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
SUITS = ["♠", "♥", "♦", "♣"]


RANK_VALUES = {rank: i for i, rank in enumerate(RANKS, start=2)}


@dataclass(frozen=True)
class Card:
    rank: str
    suit: str

    @property
    def value(self) -> int:
        """numerical value of the card rank"""
        return RANK_VALUES[self.rank]

    def __str__(self) -> str:
        """string representation of the card"""
        return f"{self.rank}{self.suit}"
