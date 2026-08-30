import unittest
from pathlib import Path
import json
import tempfile
import os

from etl.parser.cricsheet_parser import CricsheetParser, safe_get, safe_list

class TestParser(unittest.TestCase):
    def setUp(self):
        self.parser = CricsheetParser()
        
    def test_safe_get(self):
        obj = {"a": 1, "b": None}
        self.assertEqual(safe_get(obj, "a"), 1)
        self.assertIsNone(safe_get(obj, "b"))
        self.assertEqual(safe_get(obj, "c", 10), 10)
        self.assertEqual(safe_get(None, "a", "default"), "default")
        self.assertEqual(safe_get("string", "a", "default"), "default")

    def test_safe_list(self):
        self.assertEqual(safe_list([1, 2]), [1, 2])
        self.assertEqual(safe_list({"a": 1}), [])
        self.assertEqual(safe_list(None), [])
        
    def test_metadata_extraction(self):
        info = {
            "match_type": "Test",
            "dates": ["2020-01-01", "2020-01-02"],
            "teams": ["Team A", "Team B"],
            "venue": "Test Stadium",
            "toss": {"winner": "Team A", "decision": "bat"},
            "outcome": {"result": "Team A won", "winner": "Team A"},
            "player_of_match": ["Player X"]
        }
        metadata = self.parser._extract_metadata(info)
        self.assertEqual(metadata["Format"], "Test")
        self.assertEqual(metadata["Match_Date"], "2020-01-01")
        self.assertEqual(metadata["Team_1"], "Team A")
        self.assertEqual(metadata["Team_2"], "Team B")
        self.assertEqual(metadata["Venue"], "Test Stadium")
        self.assertEqual(metadata["Toss"], "Team A chose to bat")
        self.assertEqual(metadata["Result"], "Team A won")
        self.assertEqual(metadata["Player_of_the_Match"], "Player X")

    def test_metadata_extraction_dict_teams(self):
        info = {
            "teams": {"Team A": {}, "Team B": {}}
        }
        metadata = self.parser._extract_metadata(info)
        self.assertEqual(metadata["Team_1"], "Team A")
        self.assertEqual(metadata["Team_2"], "Team B")

    def test_batting_and_bowling_stats_extraction(self):
        overs = [
            {
                "deliveries": [
                    {
                        "batter": "Batter 1",
                        "bowler": "Bowler 1",
                        "runs": {"batter": 4, "extras": 0}
                    },
                    {
                        "batter": "Batter 1",
                        "bowler": "Bowler 1",
                        "runs": {"batter": 6, "extras": 0}
                    },
                    {
                        "batter": "Batter 1",
                        "bowler": "Bowler 1",
                        "runs": {"batter": 0, "extras": 1},
                        "extras": {"wides": 1}
                    }
                ]
            }
        ]
        
        batting, bowling = self.parser._extract_inning_stats(overs, 1, "Team A", "Team B")
        
        # Batting assertions
        self.assertEqual(len(batting), 1)
        bat = batting[0]
        self.assertEqual(bat["Player"], "Batter 1")
        self.assertEqual(bat["Team"], "Team A")
        self.assertEqual(bat["Runs"], 10)
        # Excludes wides from balls faced
        self.assertEqual(bat["Balls"], 2)
        self.assertEqual(bat["4s"], 1)
        self.assertEqual(bat["6s"], 1)
        
        # Bowling assertions
        self.assertEqual(len(bowling), 1)
        bowl = bowling[0]
        self.assertEqual(bowl["Player"], "Bowler 1")
        self.assertEqual(bowl["Team"], "Team B")
        self.assertEqual(bowl["Runs_Conceded"], 11)
        self.assertEqual(bowl["Balls_Bowled"], 3)
        self.assertEqual(bowl["Overs"], 0)
        self.assertEqual(bowl["Maidens"], 0)

    def test_wicket_attribution(self):
        overs = [
            {
                "deliveries": [
                    {
                        "batter": "Batter 1",
                        "bowler": "Bowler 1",
                        "runs": {"batter": 0, "extras": 0},
                        "wickets": [{"player_out": "Batter 1", "kind": "caught"}]
                    }
                ]
            }
        ]
        batting, bowling = self.parser._extract_inning_stats(overs, 1, "Team A", "Team B")
        self.assertEqual(bowling[0]["Wickets"], 1)

    def test_maiden_detection(self):
        # 6 deliveries, 0 runs
        overs = [
            {
                "deliveries": [
                    {"batter": "Batter 1", "bowler": "Bowler 1", "runs": {"batter": 0, "extras": 0}}
                    for _ in range(6)
                ]
            }
        ]
        batting, bowling = self.parser._extract_inning_stats(overs, 1, "Team A", "Team B")
        self.assertEqual(bowling[0]["Maidens"], 1)
        self.assertEqual(bowling[0]["Overs"], 1)

    def test_corrupt_json_handling(self):
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write("{invalid_json:")
            temp_path = f.name
            
        try:
            result = self.parser.parse_match(Path(temp_path))
            self.assertIsNone(result)
            self.assertEqual(len(self.parser.errors), 1)
            self.assertTrue("Failed to load" in self.parser.errors[0]["message"])
        finally:
            os.remove(temp_path)

    def test_missing_mandatory_objects(self):
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            json.dump({"info": {}}, f)
            temp_path = f.name
            
        try:
            result = self.parser.parse_match(Path(temp_path))
            self.assertIsNone(result)
            self.assertEqual(len(self.parser.errors), 1)
            self.assertTrue("Missing mandatory" in self.parser.errors[0]["message"])
        finally:
            os.remove(temp_path)


if __name__ == '__main__':
    unittest.main()
