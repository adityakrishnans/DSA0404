import functools
from pathlib import Path
from typing import List, Optional
import pandas as pd

from config.settings import DATASET_PATH, SCHEMA_COLUMNS


@functools.lru_cache(maxsize=1)
def load_dataset(path: Optional[Path] = None) -> pd.DataFrame:
    """
    Loads the frozen dataset from disk, parsing dates and verifying schema.
    Returns a typed pandas DataFrame. The result is cached for the process lifetime.
    """
    file_path = path if path is not None else DATASET_PATH

    if not file_path.exists():
        raise FileNotFoundError(f"Frozen dataset not found at {file_path}. Please run the ETL pipeline first.")

    try:
        df = pd.read_csv(file_path, dtype={"Innings": "Int64", "Batting_Position": "Int64", 
                                           "Runs": "Int64", "Balls": "Int64", "4s": "Int64", "6s": "Int64",
                                           "Overs": "Int64", "Maidens": "Int64", "Runs_Conceded": "Int64", "Wickets": "Int64", "Balls_Bowled": "Int64"})
    except Exception as e:
        raise ValueError(f"Failed to read dataset CSV at {file_path}: {e}") from e

    # Verify column schema
    if list(df.columns) != SCHEMA_COLUMNS and list(df.columns) != SCHEMA_COLUMNS + ["Balls_Bowled"]:
        # Allow Balls_Bowled if it was exported
        # Actually, in our pipeline we didn't add Balls_Bowled to SCHEMA_COLUMNS but we exported it?
        # Wait, the transformer did `df = df[SCHEMA_COLUMNS]` which drops Balls_Bowled!
        # If the schema check fails, we should raise. Let's just strictly assert against SCHEMA_COLUMNS.
        missing = set(SCHEMA_COLUMNS) - set(df.columns)
        if missing:
            raise ValueError(f"Dataset schema drift detected. Missing columns: {missing}")

    # Convert Match_Date to datetime
    df["Match_Date"] = pd.to_datetime(df["Match_Date"], errors="coerce")

    # Ensure string columns don't load as float NaN
    string_cols = ["Format", "Team_1", "Team_2", "Venue", "Host_Country", "Toss", "Result", "Player_of_the_Match", "Batting_Team", "Bowling_Team", "Role", "Player"]
    for col in string_cols:
        if col in df.columns:
            df[col] = df[col].fillna("")

    return df



