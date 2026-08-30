import unittest
import pandas as pd

from analytics.player.stats import (
    batting_career, bowling_career, batting_history, bowling_history,
    top_run_scorers, top_wicket_takers, player_of_match_count, batting_form
)
from analytics.team.stats import (
    win_loss_record, team_batting_summary, team_bowling_summary, head_to_head, runs_per_year
)
from analytics.match.stats import (
    match_scorecard, highest_team_totals, matches_per_year, venue_summary, player_of_match_by_year
)


class TestAnalytics(unittest.TestCase):
    def setUp(self):
        # Synthetic DataFrame
        data = [
            {
                "Match_ID": "1", "Match_Date": pd.to_datetime("2020-01-01"), "Format": "Test", 
                "Team_1": "Team A", "Team_2": "Team B", "Venue": "V1", "Host_Country": "C1", 
                "Toss": "A bat", "Result": "Team A won", "Player_of_the_Match": "P1",
                "Innings": 1, "Batting_Team": "Team A", "Bowling_Team": "Team B",
                "Player": "P1", "Role": "Batter", "Batting_Position": 1, 
                "Runs": 100, "Balls": 120, "4s": 10, "6s": 2, "Strike_Rate": 83.33,
                "Overs": pd.NA, "Maidens": pd.NA, "Runs_Conceded": pd.NA, "Wickets": pd.NA, "Economy": pd.NA
            },
            {
                "Match_ID": "1", "Match_Date": pd.to_datetime("2020-01-01"), "Format": "Test", 
                "Team_1": "Team A", "Team_2": "Team B", "Venue": "V1", "Host_Country": "C1", 
                "Toss": "A bat", "Result": "Team A won", "Player_of_the_Match": "P1",
                "Innings": 2, "Batting_Team": "Team B", "Bowling_Team": "Team A",
                "Player": "P2", "Role": "Bowler", "Batting_Position": pd.NA, 
                "Runs": pd.NA, "Balls": pd.NA, "4s": pd.NA, "6s": pd.NA, "Strike_Rate": pd.NA,
                "Overs": 10, "Maidens": 2, "Runs_Conceded": 30, "Wickets": 3, "Economy": 3.00
            },
            {
                "Match_ID": "2", "Match_Date": pd.to_datetime("2021-01-01"), "Format": "ODI", 
                "Team_1": "Team A", "Team_2": "Team C", "Venue": "V2", "Host_Country": "C2", 
                "Toss": "C bowl", "Result": "tie", "Player_of_the_Match": "",
                "Innings": 1, "Batting_Team": "Team A", "Bowling_Team": "Team C",
                "Player": "P1", "Role": "All-rounder", "Batting_Position": 1, 
                "Runs": 60, "Balls": 60, "4s": 5, "6s": 0, "Strike_Rate": 100.0,
                "Overs": 5, "Maidens": 0, "Runs_Conceded": 25, "Wickets": 1, "Economy": 5.00
            }
        ]
        self.df = pd.DataFrame(data)

    # --- Player Domain (8 functions) ---
    def test_batting_career(self):
        res = batting_career(self.df, "P1")
        self.assertEqual(res["Runs"], 160)
        self.assertEqual(res["100s"], 1)
        self.assertEqual(res["50s"], 1)
        self.assertEqual(res["Matches"], 2)

    def test_bowling_career(self):
        res = bowling_career(self.df, "P2")
        self.assertEqual(res["Wickets"], 3)
        self.assertEqual(res["Best_Figures"], "3-30")

    def test_batting_history(self):
        res = batting_history(self.df, "P1")
        self.assertEqual(len(res), 2)
        self.assertEqual(list(res["Runs"]), [100, 60])

    def test_bowling_history(self):
        res = bowling_history(self.df, "P1")
        self.assertEqual(len(res), 1)

    def test_top_run_scorers(self):
        res = top_run_scorers(self.df)
        self.assertEqual(res.iloc[0]["Player"], "P1")
        self.assertEqual(res.iloc[0]["Runs"], 160)

    def test_top_wicket_takers(self):
        res = top_wicket_takers(self.df)
        self.assertEqual(res.iloc[0]["Player"], "P2")
        self.assertEqual(res.iloc[0]["Wickets"], 3)

    def test_player_of_match_count(self):
        res = player_of_match_count(self.df)
        self.assertEqual(res.iloc[0]["Player"], "P1")
        self.assertEqual(res.iloc[0]["Awards"], 1)

    def test_batting_form(self):
        res = batting_form(self.df, "P1")
        self.assertEqual(len(res), 2)
        self.assertEqual(list(res["Rolling_Avg"]), [100.0, 80.0])

    # --- Team Domain (5 functions) ---
    def test_win_loss_record(self):
        res = win_loss_record(self.df, "Team A")
        self.assertEqual(res["Total_Matches"], 2)
        self.assertEqual(res["Wins"], 1)
        self.assertEqual(res["No_Result"], 1)

    def test_team_batting_summary(self):
        res = team_batting_summary(self.df, "Team A")
        self.assertEqual(len(res), 1)
        self.assertEqual(res.iloc[0]["Player"], "P1")

    def test_team_bowling_summary(self):
        res = team_bowling_summary(self.df, "Team A")
        self.assertEqual(res.iloc[0]["Wickets"], 3)

    def test_head_to_head(self):
        res = head_to_head(self.df, "Team A", "Team C")
        self.assertEqual(res["Total_Matches"], 1)

    def test_runs_per_year(self):
        res = runs_per_year(self.df, "Team A")
        self.assertEqual(len(res), 2)

    # --- Match Domain (5 functions) ---
    def test_match_scorecard(self):
        res = match_scorecard(self.df, "1")
        self.assertEqual(res["Metadata"]["Format"], "Test")
        self.assertEqual(len(res["Innings"]), 2)

    def test_highest_team_totals(self):
        res = highest_team_totals(self.df)
        self.assertEqual(res.iloc[0]["Total_Runs"], 100)

    def test_matches_per_year(self):
        res = matches_per_year(self.df)
        self.assertEqual(len(res), 2)

    def test_venue_summary(self):
        res = venue_summary(self.df)
        self.assertEqual(res.iloc[0]["Venue"], "V1")
        self.assertEqual(res.iloc[0]["Matches"], 1)

    def test_player_of_match_by_year(self):
        res = player_of_match_by_year(self.df)
        self.assertEqual(len(res), 1)

    # --- Mutation Prevention (1 test) ---
    def test_mutation_prevention(self):
        original_df = self.df.copy(deep=True)
        # Call a bunch of functions
        batting_career(self.df, "P1")
        top_run_scorers(self.df)
        win_loss_record(self.df, "Team A")
        match_scorecard(self.df, "1")
        
        # Verify the DataFrame hasn't changed at all
        pd.testing.assert_frame_equal(self.df, original_df)


if __name__ == '__main__':
    unittest.main()
