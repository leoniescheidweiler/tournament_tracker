import tkinter as tk
from tkinter import ttk


class Ui_controller:
    def __init__(self, tournament):
        self.root = None
        self.tournament = tournament
        self.tournament.register_ui_callback(self.update_ui)
        self.current_widget = None
        self.pixel = None  # needed for square buttons
        self.setup_ui()

    def setup_ui(self):
        # add root widget
        self.root = tk.Tk()
        self.root.option_add("*Font", ("Helvetica", 20))
        self.root.attributes("-fullscreen", True)
        self.styles()
        self.pixel = tk.PhotoImage()
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # add full-sized container
        self.full_frame = ttk.Frame(self.root)
        self.full_frame.grid(column=0, row=0, sticky="nswe")

        self.update_ui()

    def styles(self):
        style = ttk.Style()
        style.configure("page.TFrame", relief="solid")
        style.configure("stage.TFrame", relief="solid")
        style.configure("match.TFrame", relief="solid")

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

        center_frame = ttk.Frame(self.full_frame, padding=20, style="page.TFrame")
        self.submit_players_widget(center_frame)
        center_frame.grid(row=0, column=0)

    def ingame_widget(self):
        # add scoreboard container (left) and stages container (right)
        self.full_frame.grid_rowconfigure(0, weight=1)
        self.full_frame.grid_columnconfigure(0, weight=1)
        self.full_frame.grid_columnconfigure(1, weight=3)

        left_frame = ttk.Frame(self.full_frame, padding=20, style="page.TFrame")
        self.scoreboard_widget(left_frame)
        left_frame.grid(row=0, column=0, sticky="nswe")

        right_frame = ttk.Frame(self.full_frame, padding=20, style="page.TFrame")
        self.tournament_widget(right_frame)
        right_frame.grid(row=0, column=1, sticky="nswe")

    def postgame_widget(self):
        self.ingame_widget()

    ################################################################################################
    # SUBMIT PLAYERS
    ################################################################################################

    def submit_players_widget(self, frame):
        # populate player submission frame
        label = ttk.Label(frame, text="Enter players:", anchor="center")
        label.grid(column=0, row=0, sticky="ew")

        text_box = tk.Text(frame, height=8, width=20)
        text_box.insert(
            "1.0",
            "Olivia\nLisa\nEli\nThomas\nJakob\nLouis\nFranz\nMichi\nBen\nToffer\nJack\nKyrillis",
        )  # dummy
        text_box.grid(column=0, row=1, sticky="nswe")

        submit_button = tk.Button(
            frame,
            text="Submit",
            command=lambda: self.register_players(text_box),
        )
        submit_button.grid(column=0, row=2, sticky="ew")

    def register_players(self, text_box):
        raw_input = text_box.get("1.0", tk.END).strip()
        player_list = [p.strip() for p in raw_input.split("\n") if p]
        self.tournament.register_players(player_list)
        self.tournament.start_tournament()

    ################################################################################################
    # SCOREBOARD
    ################################################################################################

    def scoreboard_widget(self, frame):
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(0, weight=0)
        frame.grid_rowconfigure(1, weight=0)

        label = ttk.Label(frame, text="Scoreboard", anchor="center")
        label.grid(column=0, row=0, sticky="nswe")

        scoreboard_frame = ttk.Frame(frame, padding=20)
        self.populate_scoreboard(scoreboard_frame)
        scoreboard_frame.grid(column=0, row=1, sticky="nswe")

    def populate_scoreboard(self, frame):
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)
        frame.grid_columnconfigure(2, weight=1)
        frame.grid_columnconfigure(3, weight=1)
        frame.grid_columnconfigure(4, weight=1)

        # header
        header_rank = ttk.Label(frame, text="Rank", anchor="center")
        header_name = ttk.Label(frame, text="Name", anchor="center")
        header_score = ttk.Label(frame, text="Score", anchor="center")
        header_tiebreak = ttk.Label(frame, text="Tie breaker", anchor="center")
        header_rank.grid(column=0, row=0)
        header_name.grid(column=1, row=0)
        header_score.grid(column=2, row=0)
        # header_score.grid(column=2, row=0, columnspan=2)
        header_tiebreak.grid(column=4, row=0)

        # entries
        for i, player in enumerate(self.tournament.sort_players()):
            player_rank = ttk.Label(frame, text=i + 1, anchor="center")
            player_label = ttk.Label(frame, text=player.name, anchor="center")
            player_score = ttk.Label(frame, text=player.score, anchor="center")
            # if self.tournament.state != "postgame":
            #     player_pending = ttk.Label(frame, text=f"(+{player.pending_score})", anchor="center")
            player_buchholz = ttk.Label(
                frame, text=player.calculate_buchholz_score(), anchor="center"
            )
            player_rank.grid(column=0, row=i + 1)
            player_label.grid(column=1, row=i + 1)
            player_score.grid(column=2, row=i + 1)
            # if self.tournament.state != "postgame":
            #     player_pending.grid(column=3, row=i + 1)
            player_buchholz.grid(column=4, row=i + 1)

    ################################################################################################
    # STAGES
    ################################################################################################

    def tournament_widget(self, frame):
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(0, weight=0)
        frame.grid_rowconfigure(1, weight=1)

        header_frame = ttk.Frame(frame)
        self.populate_tournament_header(header_frame)
        header_frame.grid(column=0, row=0, sticky="we")

        outer_content_frame, content_frame = self.scrollableFrame(frame)
        self.populate_tournament_content(content_frame)
        outer_content_frame.grid(column=0, row=1, sticky="nswe")

    def populate_tournament_header(self, frame):
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

    def populate_tournament_content(self, frame):
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(0, weight=1)

        stages_frame = ttk.Frame(frame, padding=20)
        stages_frame.grid_columnconfigure(0, weight=1)

        for i, stage in enumerate(self.tournament.stages):
            stages_frame.grid_rowconfigure(i, minsize=175, weight=1)
            stage_frame = ttk.Frame(stages_frame, padding=10, style="stage.TFrame")
            self.populate_stage_content(stage_frame, stage)
            stage_frame.grid(column=0, row=i, sticky="nswe", padx=10, pady=10)

        stages_frame.grid(column=0, row=0, sticky="nswe")

    def populate_stage_content(self, frame, stage):
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(0, weight=0)
        stage_label = ttk.Label(frame, text=f"Stage {stage.stage_num}", anchor="center")
        i = 0
        for i, match in enumerate(stage.matches):
            frame.grid_columnconfigure(i, weight=1, uniform="a")
            frame.grid_rowconfigure(1, minsize=100, weight=1)
            match_frame = ttk.Frame(frame, padding=5, style="match.TFrame")
            self.populate_match_frame(match_frame, match)
            match_frame.grid(row=1, column=i, sticky="nswe", padx=5, pady=5)
        stage_label.grid(row=0, column=0, columnspan=i + 1, sticky="we")

    def populate_match_frame(self, frame, match):
        # P1   S1
        # BUTTONS
        # P2   S2
        frame.columnconfigure(0, weight=3)
        frame.columnconfigure(1, weight=1)
        frame.grid_rowconfigure(0, weight=2)
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_rowconfigure(2, weight=2)

        # top: player 1
        p1_label = ttk.Label(frame, text=f"{match.player_1.name}")
        p1_label.grid(column=0, row=0, sticky="nw")
        p1_score = ttk.Label(frame, text=f"{match.player_1_points}")
        p1_score.grid(column=1, row=0, sticky="ne")

        # botton: player 2
        p2_label = ttk.Label(frame, text=f"{match.player_2.name}")
        p2_label.grid(column=0, row=2, sticky="sw")
        p2_score = ttk.Label(frame, text=f"{match.player_2_points}")
        p2_score.grid(column=1, row=2, sticky="se")

        # IF stage is running: buttons inbetween
        if match.stage.state == "running":
            buttons = ttk.Frame(frame)
            self.match_buttons(buttons, match)
            buttons.grid(column=0, row=1, columnspan=2, sticky="nswe")

    def match_buttons(self, frame, match):
        frame.grid_columnconfigure(0, weight=0, uniform="a")
        frame.grid_rowconfigure(0, weight=0)
        frame.grid_rowconfigure(1, weight=0)
        frame.grid_rowconfigure(2, weight=0)
        frame.grid_rowconfigure(3, weight=0)

        if match.state == "running":
            player_1_win_button = tk.Button(
                frame,
                text="⬆️",
                image=self.pixel,
                width=25,
                height=25,
                compound="center",
                command=lambda m=match: m.register_win(match.player_1),
            )
            player_1_win_button.photo = self.pixel

            draw_button = tk.Button(
                frame,
                text="↕️",
                image=self.pixel,
                width=25,
                height=25,
                compound="center",
                command=lambda m=match: m.register_draw(),
            )
            draw_button.photo = self.pixel

            player_2_win_button = tk.Button(
                frame,
                text="⬇️",
                image=self.pixel,
                width=25,
                height=25,
                compound="center",
                command=lambda m=match: m.register_win(match.player_2),
            )
            player_2_win_button.photo = self.pixel

            player_1_win_button.grid(column=0, row=0)
            draw_button.grid(column=1, row=0)
            player_2_win_button.grid(column=2, row=0)

        if match.state == "finished":
            reset_button = tk.Button(
                frame,
                text="↩️",
                image=self.pixel,
                width=25,
                height=25,
                compound="center",
                command=lambda m=match: m.unregister_result(),
            )
            reset_button.photo = self.pixel

            reset_button.grid(column=3, row=0)

    def new_stage(self):
        self.tournament.advance_tournament()

    def scrollableFrame(self, parent):
        root = ttk.Frame(parent)

        root.grid_columnconfigure(0, weight=1)
        root.grid_columnconfigure(1, weight=0)
        root.grid_rowconfigure(0, weight=1)

        # create canvas
        canvas = tk.Canvas(root)
        canvas.grid(column=0, row=0, sticky="nswe")

        # create scrollbar
        scrollbar = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
        scrollbar.grid(column=1, row=0, sticky="ns")

        # link scrollbar to canvas
        canvas.configure(yscrollcommand=scrollbar.set)

        # create scrollable frame
        frame = ttk.Frame(canvas, padding=5)
        frame_id = canvas.create_window((0, 0), window=frame, anchor="nw")
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(frame_id, width=e.width))
        frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        return root, frame
