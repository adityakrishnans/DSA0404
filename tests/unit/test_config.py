import unittest
from pathlib import Path

from config import settings


class TestConfig(unittest.TestCase):
    def test_schema_columns_count(self):
        """Verify the schema has exactly 26 columns as per SDS."""
        self.assertEqual(len(settings.SCHEMA_COLUMNS), 26)

    def test_schema_columns_uniqueness(self):
        """Verify all column names are unique."""
        self.assertEqual(len(settings.SCHEMA_COLUMNS), len(set(settings.SCHEMA_COLUMNS)))

    def test_schema_columns_order(self):
        """Verify the exact order of columns against the SDS definition."""
        expected_columns = [
            "Match_ID", "Format", "Match_Date", "Team_1", "Team_2", "Venue",
            "Host_Country", "Toss", "Innings", "Batting_Team", "Bowling_Team",
            "Player", "Role", "Batting_Position", "Runs", "Balls", "4s", "6s",
            "Strike_Rate", "Overs", "Maidens", "Runs_Conceded", "Wickets",
            "Economy", "Result", "Player_of_the_Match"
        ]
        self.assertEqual(settings.SCHEMA_COLUMNS, expected_columns)

    def test_primary_key(self):
        """Verify the primary key definition."""
        self.assertEqual(settings.PRIMARY_KEY, ("Match_ID", "Innings", "Player"))

    def test_column_groups_coverage(self):
        """Verify that column groups contain only valid schema columns."""
        schema_set = set(settings.SCHEMA_COLUMNS)
        
        self.assertTrue(set(settings.BATTING_COLS).issubset(schema_set))
        self.assertTrue(set(settings.BOWLING_COLS).issubset(schema_set))
        self.assertTrue(set(settings.METADATA_COLS).issubset(schema_set))

    def test_valid_formats(self):
        """Verify supported formats."""
        self.assertEqual(settings.VALID_FORMATS, {"Test", "ODI"})

    def test_valid_roles(self):
        """Verify valid player roles."""
        self.assertEqual(settings.VALID_ROLES, {"Batter", "Bowler", "All-rounder"})

    def test_valid_innings(self):
        """Verify valid innings values (1-4 for Test matches)."""
        self.assertEqual(settings.VALID_INNINGS, {1, 2, 3, 4})

    def test_paths_are_pathlib_objects(self):
        """Verify that all defined paths are pathlib.Path objects."""
        self.assertIsInstance(settings.PROJECT_ROOT, Path)
        self.assertIsInstance(settings.DATA_DIR, Path)
        self.assertIsInstance(settings.SOURCE_JSON_DIR, Path)
        self.assertIsInstance(settings.DATASET_PATH, Path)

    def test_path_resolution(self):
        """Verify paths resolve to expected relative structures."""
        self.assertEqual(settings.DATA_DIR.name, "data")
        self.assertEqual(settings.DATA_DIR.parent, settings.PROJECT_ROOT)
        self.assertEqual(settings.SOURCE_JSON_DIR.name, "source")
        self.assertEqual(settings.SOURCE_JSON_DIR.parent, settings.DATA_DIR)
        
    def test_dataset_versioning(self):
        """Verify dataset version matches expected frozen value."""
        self.assertEqual(settings.DATASET_VERSION, "1.0")
        self.assertTrue(settings.DATASET_PATH.name.endswith("_v1.0.csv"))


if __name__ == '__main__':
    unittest.main()
