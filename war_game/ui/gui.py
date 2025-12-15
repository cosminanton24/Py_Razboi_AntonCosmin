import tkinter as tk
from model.engine import GameEngine


class WarGameApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("War - Card Game")

        self.engine = GameEngine()
        self.engine.reset_game()

        self.cpu_title = tk.Label(root, text="CPU", font=("Arial", 14, "bold"))
        self.cpu_title.pack(pady=(10, 0))

        self.cpu_card_label = tk.Label(root, text="--", font=("Arial", 32))
        self.cpu_card_label.pack(pady=5)

        self.player_title = tk.Label(root, text="PLAYER", font=("Arial", 14, "bold"))
        self.player_title.pack(pady=(10, 0))

        self.player_card_label = tk.Label(root, text="--", font=("Arial", 32))
        self.player_card_label.pack(pady=5)

        self.status_label = tk.Label(root, text="Press Play Round", font=("Arial", 12))
        self.status_label.pack(pady=8)

        self.score_label = tk.Label(root, text="", font=("Arial", 12))
        self.score_label.pack(pady=4)

        self.play_button = tk.Button(root, text="Play Round", command=self.on_play_round)
        self.play_button.pack(pady=6)

        self.restart_button = tk.Button(root, text="Restart", command=self.on_restart)
        self.restart_button.pack(pady=(0, 10))

        self.refresh_scores()

    def refresh_scores(self) -> None:
        p, c = self.engine.get_scores()
        self.score_label.config(text=f"Cards - Player: {p} | CPU: {c}")

    def on_play_round(self) -> None:
        if self.engine.is_game_over():
            self.status_label.config(text="Game over. Press Restart.")
            self.play_button.config(state=tk.DISABLED)
            return

        self.play_button.config(state=tk.DISABLED)

        result = self.engine.play_round()

        # Show last face-up cards involved in resolution (initial or war)
        self.player_card_label.config(text=str(result.player_card) if result.player_card else "--")
        self.cpu_card_label.config(text=str(result.cpu_card) if result.cpu_card else "--")

        self.status_label.config(text=result.message)
        self.refresh_scores()

        if result.game_over:
            self.status_label.config(text="Game over. Press Restart.")
            self.play_button.config(state=tk.DISABLED)
        else:
            self.play_button.config(state=tk.NORMAL)

    def on_restart(self) -> None:
        self.engine.reset_game()
        self.player_card_label.config(text="--")
        self.cpu_card_label.config(text="--")
        self.status_label.config(text="New game. Press Play Round.")
        self.play_button.config(state=tk.NORMAL)
        self.refresh_scores()


def run_app() -> None:
    root = tk.Tk()
    WarGameApp(root)
    root.mainloop()
