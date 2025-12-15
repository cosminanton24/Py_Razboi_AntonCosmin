from dataclasses import dataclass

# Toate rank-urile și suit-urile standard
RANKS = ["2", "3", "4", "5", "6", "7", "8", "9", "10",
         "J", "Q", "K", "A"]
SUITS = ["♠", "♥", "♦", "♣"]

# Pentru comparații: 2 = 2, ..., A = 14
RANK_VALUES = {rank: i for i, rank in enumerate(RANKS, start=2)}


@dataclass(frozen=True)
class Card:
    rank: str
    suit: str

    @property
    def value(self) -> int:
        """val numerica"""
        return RANK_VALUES[self.rank]

    def __str__(self) -> str:
        """reprezentare string a cartii"""
        return f"{self.rank}{self.suit}"
