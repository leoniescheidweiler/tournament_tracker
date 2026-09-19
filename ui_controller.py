import tkinter as tk
from tkinter import ttk


class Ui_controller:
    def __init__(self, tournament):
        self.root = None
        self.tournament = tournament
        self.tournament.register_ui_callback(self.update_ui)
        self.current_widget = None
        self.setup_ui()

    def setup_ui(self):
        # add root widget
        self.root = tk.Tk()
        self.root.option_add("*Font", ("Helvetica", 24))
        self.root.attributes("-fullscreen", True)
        self.styles()
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # add full-sized container
        self.full_frame = ttk.Frame(self.root)
        self.full_frame.grid(column=0, row=0, sticky="nsew")

        self.update_ui()

    def styles(self):
        style = ttk.Style()
        style.configure("TFrame", border=10, relief="solid")

    def update_ui(self):
        self.clear_frame(self.full_frame)
        match self.tournament.state:
            case "pregame":
                self.current_widget = self.pregame_widget
            case "ingame":
                self.current_widget = self.ingame_widget
            case "postgame":
                self.current_widget = self.postgame_widget

        self.current_widget()

    def clear_frame(self, frame):
        for widget in frame.winfo_children():
            widget.destroy()

    # MAIN WIDGETS

    def pregame_widget(self):
        # add player submission container (center)
        self.full_frame.grid_rowconfigure(0, weight=1)
        self.full_frame.grid_columnconfigure(0, weight=1)

        center_frame = ttk.Frame(self.full_frame)
        self.submit_players_widget(center_frame)
        center_frame.grid(row=0, column=0)

    def ingame_widget(self):
        # add scoreboard container (left) and stages container (right)
        self.full_frame.grid_rowconfigure(0, weight=1)
        self.full_frame.grid_columnconfigure(0, weight=1)
        self.full_frame.grid_columnconfigure(1, weight=1)

        left_frame = ttk.Frame(self.full_frame)
        self.scoreboard_widget(left_frame)
        left_frame.grid(row=0, column=0, sticky="nsew")

        right_frame = ttk.Frame(self.full_frame)
        self.stages_widget(right_frame)
        right_frame.grid(row=0, column=1, sticky="nsew")

    def postgame_widget(self):
        self.ingame_widget()

    ################################################################################################
    # SUBMIT PLAYERS
    ################################################################################################

    def submit_players_widget(self, frame):
        # populate player submission frame
        label = tk.Label(frame, text="Enter players:")
        label.grid(column=0, row=0)

        text_box = tk.Text(frame, height=8, width=20)
        text_box.insert(
            "1.0", "Olivia\nLisa\nEli\nThomas\nJakob\nLouis\nFranz\nMichi"
        )  # dummy
        text_box.grid(column=0, row=1)

        submit_button = tk.Button(
            frame,
            text="Submit",
            command=lambda: self.register_players(text_box),
        )
        submit_button.grid(column=0, row=2)

    def register_players(self, text_box):
        raw_input = text_box.get("1.0", tk.END).strip()
        player_list = [p.strip() for p in raw_input.split("\n") if p]
        self.tournament.register_players(player_list)
        self.tournament.start_tournament()

    ################################################################################################
    # SCOREBOARD
    ################################################################################################

    def scoreboard_widget(self, frame):
        label = tk.Label(frame, text="Scoreboard")
        label.grid(column=0, row=0)

        scoreboard_frame = ttk.Frame(frame)
        self.populate_scoreboard(scoreboard_frame)
        scoreboard_frame.grid(column=0, row=1)

    def populate_scoreboard(self, frame):
        # header
        header_rank = tk.Label(frame, text="Rank")
        header_name = tk.Label(frame, text="Name")
        header_score = tk.Label(frame, text="Score")
        header_tiebreak = tk.Label(frame, text="Tie breaker")
        header_rank.grid(column=0, row=0)
        header_name.grid(column=1, row=0)
        header_score.grid(column=2, row=0, columnspan=2)
        header_tiebreak.grid(column=4, row=0)

        # entries
        for i, player in enumerate(self.tournament.sort_players()):
            player_rank = tk.Label(frame, text=i + 1)
            player_label = tk.Label(frame, text=player.name)
            player_score = tk.Label(frame, text=player.score)
            if self.tournament.state != "postgame":
                player_pending = tk.Label(frame, text=f"(+{player.pending_score})")
            player_buchholz = tk.Label(frame, text=player.calculate_buchholz_score())
            player_rank.grid(column=0, row=i + 1)
            player_label.grid(column=1, row=i + 1)
            player_score.grid(column=2, row=i + 1)
            if self.tournament.state != "postgame":
                player_pending.grid(column=3, row=i + 1)
            player_buchholz.grid(column=4, row=i + 1)

    ################################################################################################
    # STAGES
    ################################################################################################

    def stages_widget(self, frame):
        frame.grid_columnconfigure(0, weight=1)

        header_frame = ttk.Frame(frame)
        self.populate_stages_header(header_frame)
        header_frame.grid(column=0, row=0, sticky="ew")

        content_frame = ttk.Frame(frame)
        self.populate_stages_frame(content_frame)
        content_frame.grid(column=0, row=1, sticky="nsew")

    def populate_stages_header(self, frame):
        if self.tournament.state != "ingame":
            return

        match self.tournament.current_stage:
            case None:
                text = "Start tournament"
            case stage if stage.stage_num <= self.tournament.max_stages:
                text = "Next stage"
            case stage if stage.stage_num == self.tournament.max_stages:
                text = "Finish tournament"

        advance_stage_button = tk.Button(
            frame,
            text=text,
            command=self.tournament.advance_tournament,
        )
        advance_stage_button.grid(column=0, row=0)

    def populate_stages_frame(self, frame):
        frame.grid_columnconfigure(0, weight=1)

        stages = self.tournament.stages
        for i, stage in enumerate(stages):
            stage_frame = ttk.Frame(frame)
            stage_frame.grid_propagate(False)
            stage_frame.config(width=1000, height=200)
            self.populate_stage_frame(stage_frame, stage)
            stage_frame.grid(column=0, row=i + 1, sticky="ew", padx=25, pady=25)

    def populate_stage_frame(self, frame, stage):
        stage_label = tk.Label(frame, text=f"Stage {stage.stage_num}")
        i = 0
        for i, match in enumerate(stage.matches):
            frame.grid_columnconfigure(i, weight=1)
            match_frame = ttk.Frame(frame)
            match_frame.grid_propagate(False)
            match_frame.config(width=200, height=150)
            self.populate_match_frame(match_frame, stage, match)
            match_frame.grid(row=1, column=i, sticky="nsew", padx=10, pady=10)
        stage_label.grid(row=0, column=0, columnspan=i + 1, sticky="nsew")

    def populate_match_frame(self, frame, stage, match):
        if stage.state == "finished":
            frame.grid_rowconfigure(0, weight=1)
            frame.grid_rowconfigure(1, weight=1)

            player_1_label = tk.Label(
                frame, text=f"{match.player_1.name} {match.player_1_points}"
            )
            player_2_label = tk.Label(
                frame, text=f"{match.player_2.name} {match.player_2_points}"
            )

            player_1_label.grid(column=0, row=0)
            player_2_label.grid(column=0, row=1)
            return

        if match.state == "running":
            frame.grid_rowconfigure(0, weight=1)
            frame.grid_rowconfigure(1, weight=1)
            frame.grid_rowconfigure(2, weight=1)
            frame.grid_columnconfigure(0, weight=1)

            player_1_win_button = tk.Button(
                frame,
                text=f"{match.player_1.name}",
                command=lambda m=match: m.register_win(match.player_1),
            )
            draw_button = tk.Button(
                frame, text="draw", command=lambda m=match: m.register_draw()
            )
            player_2_win_button = tk.Button(
                frame,
                text=f"{match.player_2.name}",
                command=lambda m=match: m.register_win(match.player_2),
            )
            player_1_win_button.grid(column=0, row=0)
            draw_button.grid(column=0, row=1)
            player_2_win_button.grid(column=0, row=2)
            return

        if match.state == "finished":
            frame.grid_columnconfigure(0, weight=1)
            frame.grid_columnconfigure(1, weight=1)
            frame.grid_rowconfigure(0, weight=1)
            frame.grid_rowconfigure(1, weight=1)

            player_1_label = tk.Label(
                frame, text=f"{match.player_1.name} {match.player_1_points}"
            )
            player_2_label = tk.Label(
                frame, text=f"{match.player_2.name} {match.player_2_points}"
            )
            reset_button = tk.Button(
                frame, text="undo", command=lambda m=match: m.unregister_result()
            )

            reset_button.grid(column=0, row=0, rowspan=2)
            player_1_label.grid(column=1, row=0)
            player_2_label.grid(column=1, row=1)
            return

    def new_stage(self):
        self.tournament.advance_tournament()
