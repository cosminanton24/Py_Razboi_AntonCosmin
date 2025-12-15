import tkinter as tk
from model.engine import GameEngine


def build_face_down_text(n: int) -> str:
    if n <= 0:
        return ""
    # simple placeholders
    return " ".join(["XX"] * n)


class WarGameApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("War - Card Game")

        self.engine = GameEngine(war_face_down_count=3)
        self.engine.reset_game()

        # CPU
        self.cpu_title = tk.Label(root, text="CPU", font=("Arial", 14, "bold"))
        self.cpu_title.pack(pady=(10, 0))

        self.cpu_down_label = tk.Label(root, text="", font=("Arial", 14))
        self.cpu_down_label.pack(pady=(2, 0))

        self.cpu_card_label = tk.Label(root, text="--", font=("Arial", 32))
        self.cpu_card_label.pack(pady=5)

        # Player
        self.player_title = tk.Label(root, text="PLAYER", font=("Arial", 14, "bold"))
        self.player_title.pack(pady=(10, 0))

        self.player_down_label = tk.Label(root, text="", font=("Arial", 14))
        self.player_down_label.pack(pady=(2, 0))

        self.player_card_label = tk.Label(root, text="--", font=("Arial", 32))
        self.player_card_label.pack(pady=5)

        # Status / scores
        self.status_label = tk.Label(root, text="Press Play", font=("Arial", 12))
        self.status_label.pack(pady=6)

        self.pot_label = tk.Label(root, text="", font=("Arial", 12))
        self.pot_label.pack(pady=2)

        self.score_label = tk.Label(root, text="", font=("Arial", 12))
        self.score_label.pack(pady=4)

        # Buttons
        self.step_button = tk.Button(root, text="Play", command=self.on_step)
        self.step_button.pack(pady=6)

        self.restart_button = tk.Button(root, text="Restart", command=self.on_restart)
        self.restart_button.pack(pady=(0, 10))

        self.refresh_scores()
        self.refresh_pot()

    def refresh_scores(self) -> None:
        p, c = self.engine.get_scores()
        self.score_label.config(text=f"Cards - Player: {p} | CPU: {c}")

    def refresh_pot(self) -> None:
        self.pot_label.config(text=f"Pot: {len(self.engine.pot)}")

    def clear_face_down(self) -> None:
        self.cpu_down_label.config(text="")
        self.player_down_label.config(text="")

    def on_step(self) -> None:
        if self.engine.state == "game_over":
            self.status_label.config(text="Game over. Press Restart.")
            self.step_button.config(state=tk.DISABLED)
            return

        self.step_button.config(state=tk.DISABLED)

        result = self.engine.next_step()

        # Update main cards (when available)
        if result.player_card is not None and result.action in ("draw", "war_up"):
            self.player_card_label.config(text=str(result.player_card))
        elif result.action == "game_over":
            pass

        if result.cpu_card is not None and result.action in ("draw", "war_up"):
            self.cpu_card_label.config(text=str(result.cpu_card))

        # War face-down placeholders
        if result.action == "war_down":
            self.player_down_label.config(text=build_face_down_text(result.player_down_count))
            self.cpu_down_label.config(text=build_face_down_text(result.cpu_down_count))

        # When a round ends, clear face-down placeholders
        if result.round_over:
            self.clear_face_down()

        # Labels
        self.status_label.config(text=result.message)
        self.refresh_scores()
        self.refresh_pot()

        # Button text reflects flow: Play starts a round, Next continues steps
        if self.engine.state == "idle":
            self.step_button.config(text="Play")
        elif self.engine.state == "game_over":
            self.step_button.config(text="Play")
        else:
            self.step_button.config(text="Next")

        if result.game_over or self.engine.state == "game_over":
            self.status_label.config(text="Game over. Press Restart.")
            self.step_button.config(state=tk.DISABLED)
        else:
            self.step_button.config(state=tk.NORMAL)

    def on_restart(self) -> None:
        self.engine.reset_game()
        self.cpu_card_label.config(text="--")
        self.player_card_label.config(text="--")
        self.clear_face_down()
        self.status_label.config(text="New game. Press Play.")
        self.step_button.config(text="Play", state=tk.NORMAL)
        self.refresh_scores()
        self.refresh_pot()


def run_app() -> None:
    root = tk.Tk()
    WarGameApp(root)
    root.mainloop()
