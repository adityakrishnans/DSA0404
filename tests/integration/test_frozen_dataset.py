import unittest
import pandas as pd
from pathlib import Path

from config.settings import DATASET_PATH
from etl.validator.dataset_validator import DatasetValidator


class TestFrozenDataset(unittest.TestCase):
    def test_frozen_dataset_passes_validation(self):
        """
        Integration test: loads the generated dataset and runs all validator checks.
        If dataset_v1.0.csv does not exist, the test is skipped.
        """
        if not DATASET_PATH.exists():
            self.skipTest(f"Frozen dataset not found at {DATASET_PATH}. Run pipeline first.")
            
        df = pd.read_csv(DATASET_PATH)
        
        # When loaded from CSV without explicit types, we need to convert na appropriately
        # But validator mostly checks schema, non-blank mandatory fields, bounds, etc.
        # Let's clean up NaNs just for validation (read_csv treats empty strings as NaNs sometimes)
        string_cols = ["Format", "Match_Date", "Team_1", "Team_2", "Venue", "Host_Country", "Toss", "Result", "Player_of_the_Match", "Batting_Team", "Bowling_Team", "Role"]
        for col in string_cols:
            if col in df.columns:
                df[col] = df[col].fillna("")
                
        validator = DatasetValidator()
        result = validator.validate(df)
        
        if not result.passed:
            result.log_failures()
            
        self.assertTrue(result.passed, "Dataset failed validation checks")


if __name__ == '__main__':
    unittest.main()
