import unittest
import pandas as pd

from config.settings import SCHEMA_COLUMNS
from etl.transformer.fact_table_builder import build_fact_table

class TestTransformer(unittest.TestCase):
    def setUp(self):
        self.metadata = [
            {
                "Match_ID": "1001",
                "Format": "Test",
                "Match_Date": "2020-01-01",
                "Team_1": "Team A",
                "Team_2": "Team B",
                "Venue": "Lord's",
                "Toss": "Team A chose to bat",
                "Result": "Team A won",
                "Player_of_the_Match": "Player 1"
            }
        ]
        
        self.batting = [
            {
                "Match_ID": "1001",
                "Innings": 1,
                "Team": "Team A",
                "Player": "Player 1",
                "Runs": 50,
                "Balls": 60,
                "4s": 5,
                "6s": 1
            },
            {
                "Match_ID": "1001",
                "Innings": 1,
                "Team": "Team A",
                "Player": "Player 2",
                "Runs": 20,
                "Balls": 30,
                "4s": 2,
                "6s": 0
            }
        ]
        
        self.bowling = [
            {
                "Match_ID": "1001",
                "Innings": 1,
                "Team": "Team B",
                "Player": "Player 3",
                "Overs": 10,
                "Maidens": 2,
                "Runs_Conceded": 40,
                "Wickets": 2,
                "Balls_Bowled": 60
            },
            # All-rounder case: Player 1 bowled in innings 2
            {
                "Match_ID": "1001",
                "Innings": 2,
                "Team": "Team A",
                "Player": "Player 1",
                "Overs": 5,
                "Maidens": 0,
                "Runs_Conceded": 25,
                "Wickets": 1,
                "Balls_Bowled": 30
            }
        ]

    def test_build_fact_table_schema(self):
        df = build_fact_table(self.metadata, self.batting, self.bowling)
        self.assertEqual(list(df.columns), SCHEMA_COLUMNS)

    def test_build_fact_table_row_count(self):
        df = build_fact_table(self.metadata, self.batting, self.bowling)
        # 2 batting rows + 2 bowling rows (1 is separate inning).
        # Innings 1: Player 1 (Bat), Player 2 (Bat), Player 3 (Bowl)
        # Innings 2: Player 1 (Bowl)
        # Total distinct (Match_ID, Innings, Player) pairs = 4
        self.assertEqual(len(df), 4)

    def test_role_assignment(self):
        df = build_fact_table(self.metadata, self.batting, self.bowling)
        
        # Player 2 is Batter only
        p2_role = df[(df["Player"] == "Player 2")]["Role"].iloc[0]
        self.assertEqual(p2_role, "Batter")
        
        # Player 3 is Bowler only
        p3_role = df[(df["Player"] == "Player 3")]["Role"].iloc[0]
        self.assertEqual(p3_role, "Bowler")
        
        # Player 1 is Batter in Innings 1, Bowler in Innings 2.
        # So in Innings 1 they are a Batter.
        p1_in1_role = df[(df["Player"] == "Player 1") & (df["Innings"] == 1)]["Role"].iloc[0]
        self.assertEqual(p1_in1_role, "Batter")

    def test_all_rounder_role(self):
        # Let's add bowling stats for Player 1 in Innings 1 to test All-rounder
        bowling_extra = [
            {
                "Match_ID": "1001",
                "Innings": 1,
                "Team": "Team A",  # Normally wouldn't bowl to own team, but for test
                "Player": "Player 1",
                "Overs": 1,
                "Maidens": 0,
                "Runs_Conceded": 5,
                "Wickets": 0,
                "Balls_Bowled": 6
            }
        ]
        df = build_fact_table(self.metadata, self.batting, self.bowling + bowling_extra)
        p1_role = df[(df["Player"] == "Player 1") & (df["Innings"] == 1)]["Role"].iloc[0]
        self.assertEqual(p1_role, "All-rounder")

    def test_derived_columns(self):
        df = build_fact_table(self.metadata, self.batting, self.bowling)
        
        # Strike rate
        p1_bat = df[(df["Player"] == "Player 1") & (df["Innings"] == 1)].iloc[0]
        self.assertEqual(p1_bat["Strike_Rate"], 83.33)  # 50/60 * 100
        
        # Economy
        p3_bowl = df[(df["Player"] == "Player 3")].iloc[0]
        self.assertEqual(p3_bowl["Economy"], 4.00)  # 40/10
        
        # Host Country
        self.assertEqual(p1_bat["Host_Country"], "England")

    def test_potm_attribution(self):
        df = build_fact_table(self.metadata, self.batting, self.bowling)
        p1_bat = df[(df["Player"] == "Player 1") & (df["Innings"] == 1)].iloc[0]
        p2_bat = df[(df["Player"] == "Player 2") & (df["Innings"] == 1)].iloc[0]
        
        self.assertEqual(p1_bat["Player_of_the_Match"], "Player 1")
        self.assertEqual(p2_bat["Player_of_the_Match"], "")

    def test_empty_inputs(self):
        df = build_fact_table([], [], [])
        self.assertEqual(len(df), 0)
        self.assertEqual(list(df.columns), SCHEMA_COLUMNS)

    def test_batting_position(self):
        df = build_fact_table(self.metadata, self.batting, self.bowling)
        
        p1_pos = df[(df["Player"] == "Player 1") & (df["Innings"] == 1)]["Batting_Position"].iloc[0]
        p2_pos = df[(df["Player"] == "Player 2") & (df["Innings"] == 1)]["Batting_Position"].iloc[0]
        p3_pos = df[(df["Player"] == "Player 3") & (df["Innings"] == 1)]["Batting_Position"].iloc[0]
        
        self.assertEqual(p1_pos, 1)
        self.assertEqual(p2_pos, 2)
        self.assertTrue(pd.isna(p3_pos))

    def test_type_preservation(self):
        df = build_fact_table(self.metadata, self.batting, self.bowling)
        
        self.assertTrue(isinstance(df["Runs"].dtype, pd.Int64Dtype))
        self.assertTrue(isinstance(df["Overs"].dtype, pd.Int64Dtype))
        
        # Batters have NaNs in bowling columns
        p1_bat = df[(df["Player"] == "Player 1") & (df["Innings"] == 1)].iloc[0]
        self.assertTrue(pd.isna(p1_bat["Overs"]))


if __name__ == '__main__':
    unittest.main()
