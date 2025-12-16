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
        self.root.minsize(520, 520)

        self.engine = GameEngine(war_face_down_count=3)
        self.engine.reset_game()

        # Flow control
        self.is_busy = False

        # Timing (ms)
        self.DELAY_DRAW = 650
        self.DELAY_COMPARE = 450
        self.DELAY_WAR_START = 600
        self.DELAY_WAR_DOWN = 700
        self.DELAY_WAR_UP = 700
        self.DELAY_AWARD = 900

        # Simple theme
        self.bg = "#0f172a"     
        self.panel = "#111827"   
        self.card_bg = "#0b1220" 
        self.text = "#e5e7eb"    
        self.muted = "#9ca3af"   

        self.root.configure(bg=self.bg)

        #top title
        title = tk.Label(
            root,
            text="WAR",
            font=("Arial", 22, "bold"),
            bg=self.bg,
            fg=self.text
        )
        title.pack(pady=(14, 6))

        subtitle = tk.Label(
            root,
            text="Player vs CPU",
            font=("Arial", 11),
            bg=self.bg,
            fg=self.muted
        )
        subtitle.pack(pady=(0, 10))

        #main board 
        self.board = tk.Frame(root, bg=self.bg)
        self.board.pack(fill="both", expand=True, padx=16, pady=10)

        #CPU area
        self.cpu_area = self._build_player_area(self.board, "CPU")
        self.cpu_area.pack(fill="x", pady=(0, 12))

        #Center status area
        self.center_area = tk.Frame(self.board, bg=self.panel, bd=0, highlightthickness=0)
        self.center_area.pack(fill="x", pady=(0, 12))

        self._build_center_area(self.center_area)

        #Player area
        self.player_area = self._build_player_area(self.board, "PLAYER")
        self.player_area.pack(fill="x")

        #Bottom controls
        self.controls = tk.Frame(root, bg=self.bg)
        self.controls.pack(fill="x", padx=16, pady=(10, 14))

        self.play_button = tk.Button(
            self.controls,
            text="Play",
            command=self.on_play,
            font=("Arial", 12, "bold"),
            padx=16,
            pady=8
        )
        self.play_button.pack(side="left")

        self.restart_button = tk.Button(
            self.controls,
            text="Restart",
            command=self.on_restart,
            font=("Arial", 12),
            padx=16,
            pady=8
        )
        self.restart_button.pack(side="left", padx=(10, 0))

        self.score_label = tk.Label(
            self.controls,
            text="",
            font=("Arial", 12),
            bg=self.bg,
            fg=self.text
        )
        self.score_label.pack(side="right")

        # Map labels for easy update
        self.cpu_card_label = self.cpu_area.card_label
        self.cpu_down_label = self.cpu_area.down_label

        self.player_card_label = self.player_area.card_label
        self.player_down_label = self.player_area.down_label

        self.refresh_scores()
        self.refresh_pot()
        self._push_log("New game. Press Play.")

        # Button states
        self._apply_button_style(self.play_button, primary=True)
        self._apply_button_style(self.restart_button, primary=False)

    #ui builders

    def _build_player_area(self, parent: tk.Widget, name: str) -> tk.Frame:
        frame = tk.Frame(parent, bg=self.panel, padx=14, pady=12)
        frame.configure(highlightthickness=0)

        header = tk.Frame(frame, bg=self.panel)
        header.pack(fill="x")

        name_label = tk.Label(
            header,
            text=name,
            font=("Arial", 13, "bold"),
            bg=self.panel,
            fg=self.text
        )
        name_label.pack(side="left")

        down_label = tk.Label(
            frame,
            text="",
            font=("Consolas", 12),
            bg=self.panel,
            fg=self.muted
        )
        down_label.pack(anchor="w", pady=(8, 6))

        # Card slot
        slot = tk.Frame(
            frame,
            bg=self.card_bg,
            bd=0,
            highlightbackground="#334155",
            highlightthickness=2,
            padx=10,
            pady=10
        )
        slot.pack(fill="x")

        card_label = tk.Label(
            slot,
            text="--",
            font=("Arial", 36, "bold"),
            bg=self.card_bg,
            fg=self.text
        )
        card_label.pack()

        # Attach for easy access
        frame.down_label = down_label
        frame.card_label = card_label
        return frame

    def _build_center_area(self, parent: tk.Widget) -> None:
        parent.configure(padx=14, pady=12, bg=self.panel)

        top = tk.Frame(parent, bg=self.panel)
        top.pack(fill="x")

        self.pot_label = tk.Label(
            top,
            text="Pot: 0",
            font=("Arial", 12, "bold"),
            bg=self.panel,
            fg=self.text
        )
        self.pot_label.pack(side="left")

        self.status_label = tk.Label(
            top,
            text="",
            font=("Arial", 12),
            bg=self.panel,
            fg=self.muted
        )
        self.status_label.pack(side="right")

        # Log box
        self.log_box = tk.Text(
            parent,
            height=5,
            wrap="word",
            font=("Consolas", 10),
            bg=self.card_bg,
            fg=self.text,
            bd=0,
            highlightthickness=2,
            highlightbackground="#334155"
        )
        self.log_box.pack(fill="x", pady=(10, 0))
        self.log_box.config(state="disabled")

    def _apply_button_style(self, btn: tk.Button, primary: bool) -> None:
        if primary:
            btn.configure(
                bg="#2563eb",
                fg="white",
                activebackground="#1d4ed8",
                activeforeground="white",
                relief="flat",
                bd=0
            )
        else:
            btn.configure(
                bg="#374151",
                fg="white",
                activebackground="#4b5563",
                activeforeground="white",
                relief="flat",
                bd=0
            )

    #UI helpers

    def refresh_scores(self) -> None:
        p, c = self.engine.get_scores()
        self.score_label.config(text=f"Cards  Player: {p}   CPU: {c}")

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
            if self.engine.state == "game_over":
                self.play_button.config(state=tk.DISABLED)
            else:
                self.play_button.config(state=tk.NORMAL)

    def _push_log(self, line: str) -> None:
        self.log_box.config(state="normal")
        content = self.log_box.get("1.0", "end").strip().splitlines()
        if content == [""]:
            content = []
        content.append(line)
        content = content[-5:]

        self.log_box.delete("1.0", "end")
        self.log_box.insert("1.0", "\n".join(content) + "\n")
        self.log_box.config(state="disabled")
        self.log_box.see("end")

    #Game flow

    def on_play(self) -> None:
        if self.is_busy:
            return
        if self.engine.state == "game_over":
            self.status_label.config(text="Game over.")
            self.play_button.config(state=tk.DISABLED)
            return

        self.set_busy(True)
        self._animate_round_step()

    def _animate_round_step(self) -> None:
        result = self.engine.next_step()

        # Update cards on draw and war_up
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
        self.status_label.config(text=result.action.upper())
        self.refresh_scores()
        self.refresh_pot()

        # Log messages
        if result.message:
            self._push_log(result.message)

        # Stop conditions
        if result.game_over or self.engine.state == "game_over":
            self._push_log("Game over. Press Restart.")
            self.status_label.config(text="GAME OVER")
            self.set_busy(False)
            self.play_button.config(state=tk.DISABLED)
            return

        if self.engine.state == "idle":
            # Round finished
            self.set_busy(False)
            return

        delay = self._delay_for_action(result.action)
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
        return 500

    def on_restart(self) -> None:
        if self.is_busy:
            return

        self.engine.reset_game()
        self.cpu_card_label.config(text="--")
        self.player_card_label.config(text="--")
        self.clear_face_down()
        self.status_label.config(text="READY")
        self.refresh_scores()
        self.refresh_pot()

        # Clear log
        self.log_box.config(state="normal")
        self.log_box.delete("1.0", "end")
        self.log_box.config(state="disabled")
        self._push_log("New game. Press Play.")

        self.play_button.config(state=tk.NORMAL)


def run_app() -> None:
    root = tk.Tk()
    WarGameApp(root)
    root.mainloop()
