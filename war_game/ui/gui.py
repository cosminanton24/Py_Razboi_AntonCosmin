import tkinter as tk
from model.engine import GameEngine


class WarGameApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("War - Card Game")

        # Creăm engine-ul jocului și îl resetam
        self.engine = GameEngine()
        self.engine.reset_game()

        # Label simplu ca sa vedem ca totul merge
        self.info_label = tk.Label(
            root,
            text="War Game - setup OK\nApasa butonul pentru a vedea scorurile initiale."
        )
        self.info_label.pack(padx=20, pady=10)

        self.show_scores_button = tk.Button(
            root,
            text="Arata scoruri",
            command=self.show_scores
        )
        self.show_scores_button.pack(pady=5)

    def show_scores(self) -> None:
        player_count, cpu_count = self.engine.get_scores()
        self.info_label.config(
            text=f"Scor initial:\nPlayer: {player_count} carti\nCPU: {cpu_count} carti"
        )


def run_app() -> None:
    root = tk.Tk()
    app = WarGameApp(root)
    root.mainloop()
