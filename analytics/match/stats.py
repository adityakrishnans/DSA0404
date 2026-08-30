import pandas as pd
from typing import Optional, Dict


def match_scorecard(df: pd.DataFrame, match_id: str) -> Dict:
    mask = df["Match_ID"].astype(str) == str(match_id) # ensure string comparison
    match_df = df[mask].copy()
    
    if match_df.empty:
        return {}
        
    # Extract metadata from the first row
    first_row = match_df.iloc[0]
    metadata = {
        "Match_ID": first_row["Match_ID"],
        "Format": first_row["Format"],
        "Match_Date": first_row["Match_Date"],
        "Team_1": first_row["Team_1"],
        "Team_2": first_row["Team_2"],
        "Venue": first_row["Venue"],
        "Toss": first_row["Toss"],
        "Result": first_row["Result"],
        "Player_of_the_Match": first_row["Player_of_the_Match"]
    }
    
    innings_list = []
    # Group by Innings
    for inning_num, inning_df in match_df.groupby("Innings"):
        # Batting
        batting_df = inning_df[inning_df["Runs"].notna()].sort_values("Batting_Position")
        batting = batting_df[["Player", "Batting_Position", "Runs", "Balls", "4s", "6s", "Strike_Rate"]]
        
        # Bowling
        bowling_df = inning_df[inning_df["Overs"].notna()]
        bowling = bowling_df[["Player", "Overs", "Maidens", "Runs_Conceded", "Wickets", "Economy"]]
        
        totals = {
            "Total_Runs": int(batting_df["Runs"].sum()) if not batting_df.empty else 0,
            "Wickets_Fallen": int(bowling_df["Wickets"].sum()) if not bowling_df.empty else 0,
            "Batting_Team": batting_df["Batting_Team"].iloc[0] if not batting_df.empty else "",
            "Bowling_Team": bowling_df["Bowling_Team"].iloc[0] if not bowling_df.empty else ""
        }
        
        innings_list.append({
            "Inning": inning_num,
            "Batting": batting,
            "Bowling": bowling,
            "Totals": totals
        })
        
    return {
        "Metadata": metadata,
        "Innings": innings_list
    }


def highest_team_totals(df: pd.DataFrame, format_: Optional[str] = None, top_n: int = 10) -> pd.DataFrame:
    mask = df["Runs"].notna()
    if format_:
        mask &= df["Format"] == format_
        
    batting_df = df[mask]
    if batting_df.empty:
        return pd.DataFrame()
        
    # We also need wickets fallen, which is sum of wickets from bowling
    bowling_df = df[df["Overs"].notna()]
    if format_:
        bowling_df = bowling_df[bowling_df["Format"] == format_]
        
    runs_grouped = batting_df.groupby(["Match_ID", "Innings", "Batting_Team", "Match_Date"]).agg(
        Total_Runs=("Runs", "sum")
    ).reset_index()
    
    wkts_grouped = bowling_df.groupby(["Match_ID", "Innings", "Bowling_Team"]).agg(
        Wickets_Fallen=("Wickets", "sum")
    ).reset_index()
    
    # Merge them. Batting_Team == Bowling_Team's opponent, so we can just join on Match_ID and Innings
    merged = pd.merge(runs_grouped, wkts_grouped[["Match_ID", "Innings", "Bowling_Team", "Wickets_Fallen"]], 
                      on=["Match_ID", "Innings"], how="left")
    
    top = merged.sort_values("Total_Runs", ascending=False).head(top_n)
    top["Total_Runs"] = top["Total_Runs"].astype("Int64")
    top["Wickets_Fallen"] = top["Wickets_Fallen"].fillna(0).astype("Int64")
    
    return top[["Match_ID", "Innings", "Batting_Team", "Bowling_Team", "Match_Date", "Total_Runs", "Wickets_Fallen"]]


def matches_per_year(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()
        
    matches = df.drop_duplicates(subset=["Match_ID"]).copy()
    
    if pd.api.types.is_datetime64_any_dtype(matches["Match_Date"]):
        matches["Year"] = matches["Match_Date"].dt.year
    else:
        matches["Year"] = matches["Match_Date"].str[:4].astype(int)
        
    grouped = matches.groupby(["Year", "Format"]).size().reset_index(name="Matches")
    return grouped.sort_values("Year")


def venue_summary(df: pd.DataFrame, format_: Optional[str] = None, top_n: int = 15) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()
        
    mask = pd.Series(True, index=df.index)
    if format_:
        mask &= df["Format"] == format_
        
    filtered = df[mask]
    if filtered.empty:
        return pd.DataFrame()
        
    matches = filtered.drop_duplicates(subset=["Match_ID"])
    
    venue_matches = matches.groupby(["Venue", "Host_Country"]).size().rename("Matches")
    
    # Total runs at venue
    batting = filtered[filtered["Runs"].notna()]
    venue_runs = batting.groupby(["Venue", "Host_Country"])["Runs"].sum().rename("Total_Runs")
    
    merged = pd.DataFrame(venue_matches).join(venue_runs).reset_index()
    merged["Total_Runs"] = merged["Total_Runs"].fillna(0).astype("Int64")
    
    return merged.sort_values("Matches", ascending=False).head(top_n)


def player_of_match_by_year(df: pd.DataFrame, format_: Optional[str] = None) -> pd.DataFrame:
    mask = df["Player_of_the_Match"] != ""
    if format_:
        mask &= df["Format"] == format_
        
    awards = df[mask].drop_duplicates(subset=["Match_ID"]).copy()
    if awards.empty:
        return pd.DataFrame()
        
    if pd.api.types.is_datetime64_any_dtype(awards["Match_Date"]):
        awards["Year"] = awards["Match_Date"].dt.year
    else:
        awards["Year"] = awards["Match_Date"].str[:4].astype(int)
        
    counts = awards.groupby("Year").size().reset_index(name="Awards_Given")
    return counts.sort_values("Year")
