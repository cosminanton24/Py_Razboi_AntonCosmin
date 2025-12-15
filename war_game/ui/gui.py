import tkinter as tk
from model.engine import GameEngine


def build_face_down_text(n: int) -> str:
    if n <= 0:
        return ""
    return " ".join(["XX"] * n)


class WarGameApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("War - Card Game")

        self.engine = GameEngine(war_face_down_count=3)
        self.engine.reset_game()

        # Animation / flow control
        self.is_busy = False

        # Timing (ms)
        self.DELAY_DRAW = 600
        self.DELAY_COMPARE = 450
        self.DELAY_WAR_START = 550
        self.DELAY_WAR_DOWN = 650
        self.DELAY_WAR_UP = 650
        self.DELAY_AWARD = 800

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
        self.play_button = tk.Button(root, text="Play", command=self.on_play)
        self.play_button.pack(pady=6)

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

    def set_busy(self, busy: bool) -> None:
        self.is_busy = busy
        if busy:
            self.play_button.config(state=tk.DISABLED)
        else:
            # Only enable if game not over
            if self.engine.state == "game_over":
                self.play_button.config(state=tk.DISABLED)
            else:
                self.play_button.config(state=tk.NORMAL)

    def on_play(self) -> None:
        if self.is_busy:
            return
        if self.engine.state == "game_over":
            self.status_label.config(text="Game over. Press Restart.")
            self.play_button.config(state=tk.DISABLED)
            return

        self.set_busy(True)
        # Start a full round animation sequence
        self._animate_round_step()

    def _animate_round_step(self) -> None:
        """
        Runs engine.next_step() and schedules the next step based on the returned action/state.
        Continues until round ends (engine.state becomes idle) or game over.
        """
        result = self.engine.next_step()

        # Update cards shown for draw and war_up
        if result.action in ("draw", "war_up"):
            if result.player_card is not None:
                self.player_card_label.config(text=str(result.player_card))
            if result.cpu_card is not None:
                self.cpu_card_label.config(text=str(result.cpu_card))

        # War down placeholders
        if result.action == "war_down":
            self.player_down_label.config(text=build_face_down_text(result.player_down_count))
            self.cpu_down_label.config(text=build_face_down_text(result.cpu_down_count))

        # Clear placeholders when round ends
        if result.round_over:
            self.clear_face_down()

        # Status + counters
        self.status_label.config(text=result.message)
        self.refresh_scores()
        self.refresh_pot()

        # Stop conditions
        if result.game_over or self.engine.state == "game_over":
            self.status_label.config(text="Game over. Press Restart.")
            self.set_busy(False)
            self.play_button.config(state=tk.DISABLED)
            return

        if self.engine.state == "idle":
            # Round fully finished
            self.set_busy(False)
            return

        # Decide delay for the next scheduled step
        delay = self._delay_for_action(result.action)

        # Schedule next step
        self.root.after(delay, self._animate_round_step)

    def _delay_for_action(self, action: str) -> int:
        if action == "draw":
            return self.DELAY_DRAW
        if action == "compare":
            return self.DELAY_COMPARE
        if action == "war_start":
            return self.DELAY_WAR_START
        if action == "war_down":
            return self.DELAY_WAR_DOWN
        if action == "war_up":
            return self.DELAY_WAR_UP
        if action == "award":
            return self.DELAY_AWARD
        # default
        return 500

    def on_restart(self) -> None:
        if self.is_busy:
            # ignore restart during animation (minimal safeguard)
            return

        self.engine.reset_game()
        self.cpu_card_label.config(text="--")
        self.player_card_label.config(text="--")
        self.clear_face_down()
        self.status_label.config(text="New game. Press Play.")
        self.refresh_scores()
        self.refresh_pot()
        self.play_button.config(text="Play", state=tk.NORMAL)


def run_app() -> None:
    root = tk.Tk()
    WarGameApp(root)
    root.mainloop()
