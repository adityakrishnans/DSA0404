from pathlib import Path

# Absolute paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
SOURCE_JSON_DIR = DATA_DIR / "source"

# Dataset Version
DATASET_VERSION = "1.0"
DATASET_FILENAME = f"dataset_v{DATASET_VERSION}.csv"
DATASET_PATH = DATA_DIR / DATASET_FILENAME

# Schema constants (SDS 4.2)
SCHEMA_COLUMNS = [
    "Match_ID", "Format", "Match_Date", "Team_1", "Team_2", "Venue",
    "Host_Country", "Toss", "Innings", "Batting_Team", "Bowling_Team",
    "Player", "Role", "Batting_Position", "Runs", "Balls", "4s", "6s",
    "Strike_Rate", "Overs", "Maidens", "Runs_Conceded", "Wickets",
    "Economy", "Result", "Player_of_the_Match"
]

PRIMARY_KEY = ("Match_ID", "Innings", "Player")

# Column groups for logical validation and analytics
BATTING_COLS = [
    "Batting_Position", "Runs", "Balls", "4s", "6s", "Strike_Rate"
]

BOWLING_COLS = [
    "Overs", "Maidens", "Runs_Conceded", "Wickets", "Economy"
]

METADATA_COLS = [
    "Match_ID", "Format", "Match_Date", "Team_1", "Team_2", "Venue",
    "Host_Country", "Toss", "Result", "Player_of_the_Match"
]

# Validation constraints
VALID_FORMATS = {"Test", "ODI"}
VALID_ROLES = {"Batter", "Bowler", "All-rounder"}
VALID_INNINGS = {1, 2, 3, 4}

# Shared lookup data
VENUE_TO_COUNTRY = {
    # Major international venues will be added here
    "Lord's": "England",
    "Melbourne Cricket Ground": "Australia",
    "Eden Gardens": "India",
    # (Placeholder lookup mapping; to be expanded later)
}

