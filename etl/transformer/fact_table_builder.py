import pandas as pd
from typing import List, Dict

from config.settings import VENUE_TO_COUNTRY, SCHEMA_COLUMNS


def build_fact_table(
    all_metadata: List[Dict],
    all_batting: List[Dict],
    all_bowling: List[Dict]
) -> pd.DataFrame:
    """
    Transforms parsed Python dictionaries into the final
    26-column player-level fact table.
    """

    # 1. DataFrame Construction
    df_meta = pd.DataFrame(all_metadata)
    df_bat = pd.DataFrame(all_batting)
    df_bowl = pd.DataFrame(all_bowling)

    # Handle edge case where there is no data
    if df_meta.empty:
        return pd.DataFrame(columns=SCHEMA_COLUMNS)

    if df_bat.empty:
        df_bat = pd.DataFrame(
            columns=[
                "Match_ID", "Innings", "Team", "Player",
                "Runs", "Balls", "4s", "6s"
            ]
        )

    if df_bowl.empty:
        df_bowl = pd.DataFrame(
            columns=[
                "Match_ID", "Innings", "Team", "Player",
                "Overs", "Maidens", "Runs_Conceded",
                "Wickets", "Balls_Bowled"
            ]
        )

    # 2. Full Outer Join on batting and bowling
    df_player_innings = pd.merge(
        df_bat,
        df_bowl,
        on=["Match_ID", "Innings", "Team", "Player"],
        how="outer"
    )

    # 3. Left Join with metadata
    df = pd.merge(
        df_player_innings,
        df_meta,
        on="Match_ID",
        how="left"
    )

    # 4. Derived Columns

    # The parser already provides the actual team in "Team".
    # Therefore:
    # Runs present  -> Team is the Batting_Team
    # Overs present -> Team is the Bowling_Team

    has_batting = df["Runs"].notna()
    has_bowling = df["Overs"].notna()

    df["Batting_Team"] = ""
    df["Bowling_Team"] = ""

    df.loc[has_batting, "Batting_Team"] = df.loc[has_batting, "Team"]
    df.loc[has_bowling, "Bowling_Team"] = df.loc[has_bowling, "Team"]

    # Role
    df["Role"] = ""
    df.loc[has_batting & ~has_bowling, "Role"] = "Batter"
    df.loc[~has_batting & has_bowling, "Role"] = "Bowler"
    df.loc[has_batting & has_bowling, "Role"] = "All-rounder"

    # Batting Position
    batting_mask = df["Runs"].notna()

    df.loc[batting_mask, "Batting_Position"] = (
        df[batting_mask]
        .groupby(["Match_ID", "Innings"])
        .cumcount() + 1
    )

    # Strike Rate
    df["Strike_Rate"] = (
        df["Runs"] / df["Balls"] * 100
    ).round(2)

    # Economy
    if "Balls_Bowled" in df.columns:
        overs_exact = df["Balls_Bowled"] / 6

        df["Economy"] = (
            df["Runs_Conceded"]
            / overs_exact.replace(0, pd.NA)
        ).round(2)
    else:
        df["Economy"] = pd.NA

    # Host Country
    df["Host_Country"] = (
        df["Venue"]
        .map(VENUE_TO_COUNTRY)
        .fillna("")
    )

    # Player of the Match validation
    df["Player_of_the_Match"] = df.apply(
        lambda row:
        row["Player"]
        if row["Player"] == row["Player_of_the_Match"]
        else "",
        axis=1
    )

    # 5. Missing values and type preservation

    # Fill strings
    string_cols = [
        "Format",
        "Match_Date",
        "Team_1",
        "Team_2",
        "Venue",
        "Host_Country",
        "Toss",
        "Result",
        "Player_of_the_Match",
        "Batting_Team",
        "Bowling_Team",
        "Role"
    ]

    for col in string_cols:
        if col in df.columns:
            df[col] = df[col].fillna("")

    # Convert integer columns to nullable Int64
    int_cols = [
        "Innings",
        "Batting_Position",
        "Runs",
        "Balls",
        "4s",
        "6s",
        "Overs",
        "Maidens",
        "Runs_Conceded",
        "Wickets"
    ]

    for col in int_cols:
        if col in df.columns:
            df[col] = df[col].astype(pd.Int64Dtype())

    # Ensure schema order
    df = df[SCHEMA_COLUMNS]

    return df