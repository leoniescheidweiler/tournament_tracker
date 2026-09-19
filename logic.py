import numpy as np
import random


class Tournament:
    def __init__(self):
        self.state = "pregame"  # pregame, ingame, postgame
        self.players = []
        self.player_num = None
        self.max_stages = 0
        self.stages = []
        self.current_stage_index = None
        self.current_stage = None
        self.victory_points = 3
        self.draw_points = 1
        self.defeat_points = 0
        self.ui_callback = None

    def register_ui_callback(self, callback):
        self.ui_callback = callback

    def notify_ui(self):
        if self.ui_callback:
            self.ui_callback()

    def register_players(self, players):
        print("Registering players")
        random.shuffle(players)
        for player in players:
            self.players.append(Player(player))
        self.player_num = len(self.players)
        self.max_stages = int(np.ceil(np.log2(self.player_num)))
        self.notify_ui()

    def start_tournament(self):
        print("Starting tournament")
        for i in range(self.max_stages):
            stage_num = i + 1
            self.stages.append(Stage(self, stage_num))
        self.state = "ingame"
        self.notify_ui()

    def advance_tournament(self):
        if self.state != "ingame":
            print(f"Error: State must be ingame, is currently {self.state}.")
            return

        if self.current_stage_index == None:
            print("Starting first stage.")
            self.current_stage_index = 0
            self.current_stage = self.stages[self.current_stage_index]
            self.current_stage.start_stage()
            self.notify_ui()
            return

        if self.current_stage_index + 1 < self.max_stages:
            print("Finishing current stage.")
            self.current_stage.finish_stage()

            if not self.current_stage.state == "finished":
                print("Error: Current stage is still running.")
                return

            print("Starting next stage.")
            self.current_stage_index += 1
            self.current_stage = self.stages[self.current_stage_index]
            self.current_stage.start_stage()
            self.notify_ui()
            return

        if self.current_stage_index + 1 == self.max_stages:
            print("Finishing current stage.")
            self.current_stage.finish_stage()

            if not self.current_stage.state == "finished":
                print("Error: Current stage is still running.")
                return

            print("No more stages. Ending tournament.")
            self.current_stage_index = None
            self.current_stage = None
            self.notify_ui()

            self.end_tournament()

    def end_tournament(self):
        self.state = "postgame"
        self.notify_ui()

    def sort_players(self):
        scores = [p.score for p in self.players]
        buchholz_scores = [p.calculate_buchholz_score() for p in self.players]

        tuples = list(zip(self.players, scores, buchholz_scores))
        sorted_tuples = sorted(tuples, key=lambda p: (-p[1], -p[2]))
        sorted_players, _, _ = zip(*sorted_tuples)
        sorted_players = list(sorted_players)

        return sorted_players


class Player:
    def __init__(self, name):
        self.name = name
        self.score = 0
        self.pending_score = 0
        self.previous_opponents = []

    def add_pending_score(self):
        self.score += self.pending_score
        self.pending_score = 0

    def calculate_buchholz_score(self):
        buchholz_score = 0
        for opponent in self.previous_opponents:
            buchholz_score += opponent.score
        return buchholz_score


class Stage:
    def __init__(self, tournament, stage_num):
        self.tournament = tournament
        self.stage_num = stage_num
        self.players = tournament.players
        self.matches = []
        self.state = "upcoming"  # upcoming, running, finished
        self.ui_callback = tournament.ui_callback

    def notify_ui(self):
        if self.ui_callback:
            self.ui_callback()

    def start_stage(self):
        if self.state != "upcoming":
            print(f"Error: Stage state should be upcoming, is currently {self.state}.")
            return

        self.state = "running"
        self.generate_matches()

    def generate_matches(self):
        print("generating matches")

        sorted_players = self.tournament.sort_players()

        while len(sorted_players) > 1:
            player = sorted_players[0]
            opponent = None
            for opponent in sorted_players[1:]:
                if opponent not in player.previous_opponents:
                    break
            self.matches.append(Match(self, player, opponent))
            sorted_players.remove(player)
            sorted_players.remove(opponent)

        if len(sorted_players) == 1:
            sorted_players[0].pending_score = self.tournament.victory_points

        self.notify_ui()

    def finish_stage(self):
        if not self.state == "running":
            print(f"Error: Stage state should be running, is currently {self.state}.")
            return

        if not all(match.state == "finished" for match in self.matches):
            print("Error: Some matches are not finished.")
            return

        print("Writing results for stage.")
        for player in self.players:
            player.add_pending_score()
        self.state = "finished"
        self.notify_ui()


class Match:
    def __init__(self, stage, player_1, player_2):
        self.player_1 = player_1
        self.player_2 = player_2
        self.player_1_points = 0
        self.player_2_points = 0
        self.stage = stage
        self.state = "running"  # "running", "finished"
        self.ui_callback = stage.ui_callback

    def notify_ui(self):
        if self.ui_callback:
            self.ui_callback()

    def register_win(self, winner):
        if not self.state == "running":
            print("Error: Match is not running.")
            return

        if winner == self.player_1:
            print(f"{self.player_1.name} wins against {self.player_2.name}.")
            self.player_1_points = self.stage.tournament.victory_points
            self.player_2_points = self.stage.tournament.defeat_points
            self.player_1.pending_score = self.player_1_points
            self.player_2.pending_score = self.player_2_points
        else:
            print(f"{self.player_2.name} wins against {self.player_1.name}.")
            self.player_2_points = self.stage.tournament.victory_points
            self.player_1_points = self.stage.tournament.defeat_points
            self.player_2.pending_score = self.player_2_points
            self.player_1.pending_score = self.player_1_points

        self.player_1.previous_opponents.append(self.player_2)
        self.player_2.previous_opponents.append(self.player_1)

        self.state = "finished"
        self.notify_ui()

    def register_draw(self):
        if not self.state == "running":
            print("Error: Match is not running.")
            return

        print(f"{self.player_1.name} and {self.player_2.name} draw.")

        self.player_1_points = self.stage.tournament.draw_points
        self.player_2_points = self.stage.tournament.draw_points
        self.player_1.pending_score = self.player_1_points
        self.player_2.pending_score = self.player_1_points

        self.player_1.previous_opponents.append(self.player_2)
        self.player_2.previous_opponents.append(self.player_1)

        self.state = "finished"
        self.notify_ui()

    def unregister_result(self):
        if not self.state == "finished":
            print("Error: Cannot reset results, as match is not finished.")

        print(
            f"Resetting result between {self.player_1.name} and {self.player_2.name}."
        )

        self.player_1_points = 0
        self.player_2_points = 0
        self.player_1.pending_score = self.player_1_points
        self.player_2.pending_score = self.player_2_points

        self.player_1.previous_opponents.remove(self.player_2)
        self.player_2.previous_opponents.remove(self.player_1)

        self.state = "running"
        self.notify_ui()
