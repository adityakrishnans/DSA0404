import pandas as pd
from typing import Optional, Dict


def win_loss_record(df: pd.DataFrame, team: str, format_: Optional[str] = None) -> Dict:
    mask = (df["Team_1"] == team) | (df["Team_2"] == team)
    if format_:
        mask &= df["Format"] == format_
        
    team_df = df[mask].drop_duplicates(subset=["Match_ID"])
    if team_df.empty:
        return {}
        
    total_matches = len(team_df)
    wins = len(team_df[team_df["Result"] == f"{team} won"])
    
    # In Cricsheet, result is either "{team} won", "no result", "tie", or blank (draw/abandoned)
    # We can infer losses as: it's not a win, and it's not a tie/no result, and it actually has a winner
    # Alternatively, any result ending in " won" where the team is not the winner is a loss.
    losses = len(team_df[team_df["Result"].str.endswith(" won") & (team_df["Result"] != f"{team} won")])
    no_results = len(team_df[team_df["Result"].isin(["no result", "tie", "drawn", "abandoned"])])
    # Also blank means draw in tests usually
    no_results += len(team_df[team_df["Result"] == ""])
    
    win_percentage = round((wins / total_matches) * 100, 2) if total_matches > 0 else 0.0
    
    return {
        "Total_Matches": total_matches,
        "Wins": wins,
        "Losses": losses,
        "No_Result": no_results,
        "Win_Percentage": win_percentage
    }


def team_batting_summary(df: pd.DataFrame, team: str, format_: Optional[str] = None) -> pd.DataFrame:
    mask = (df["Batting_Team"] == team) & df["Runs"].notna()
    if format_:
        mask &= df["Format"] == format_
        
    batting_df = df[mask]
    if batting_df.empty:
        return pd.DataFrame()
        
    grouped = batting_df.groupby("Player").agg(
        Innings=("Runs", "count"),
        Runs=("Runs", "sum"),
        Balls=("Balls", "sum"),
        Highest=("Runs", "max")
    )
    
    grouped["100s"] = batting_df[batting_df["Runs"] >= 100].groupby("Player").size()
    grouped["50s"] = batting_df[(batting_df["Runs"] >= 50) & (batting_df["Runs"] < 100)].groupby("Player").size()
    grouped = grouped.fillna(0)
    
    grouped["Strike_Rate"] = (grouped["Runs"] / grouped["Balls"] * 100).round(2).fillna(0)
    
    top = grouped.sort_values("Runs", ascending=False).reset_index()
    for col in ["Innings", "Runs", "Balls", "Highest", "100s", "50s"]:
        top[col] = top[col].astype("Int64")
        
    return top[["Player", "Innings", "Runs", "Balls", "4s", "6s", "Highest", "100s", "50s", "Strike_Rate"]] if "4s" in top.columns else top


def team_bowling_summary(df: pd.DataFrame, team: str, format_: Optional[str] = None) -> pd.DataFrame:
    mask = (df["Bowling_Team"] == team) & df["Overs"].notna()
    if format_:
        mask &= df["Format"] == format_
        
    bowling_df = df[mask]
    if bowling_df.empty:
        return pd.DataFrame()
        
    grouped = bowling_df.groupby("Player").agg(
        Innings=("Overs", "count"),
        Overs=("Overs", "sum"),
        Maidens=("Maidens", "sum"),
        Runs_Conceded=("Runs_Conceded", "sum"),
        Wickets=("Wickets", "sum")
    )
    
    grouped["Average"] = (grouped["Runs_Conceded"] / grouped["Wickets"]).round(2).fillna(0)
    grouped["Economy"] = (grouped["Runs_Conceded"] / grouped["Overs"]).round(2).fillna(0)
    
    top = grouped.sort_values("Wickets", ascending=False).reset_index()
    for col in ["Innings", "Overs", "Maidens", "Runs_Conceded", "Wickets"]:
        top[col] = top[col].astype("Int64")
        
    return top[["Player", "Innings", "Overs", "Maidens", "Runs_Conceded", "Wickets", "Economy", "Average"]]


def head_to_head(df: pd.DataFrame, team_a: str, team_b: str, format_: Optional[str] = None) -> Dict:
    mask = ((df["Team_1"] == team_a) & (df["Team_2"] == team_b)) | \
           ((df["Team_1"] == team_b) & (df["Team_2"] == team_a))
    if format_:
        mask &= df["Format"] == format_
        
    h2h_df = df[mask]
    if h2h_df.empty:
        return {}
        
    matches = h2h_df.drop_duplicates(subset=["Match_ID"])
    
    team_a_wins = len(matches[matches["Result"] == f"{team_a} won"])
    team_b_wins = len(matches[matches["Result"] == f"{team_b} won"])
    
    # Calculate total runs
    batting = h2h_df[h2h_df["Runs"].notna()]
    team_a_runs = int(batting[batting["Batting_Team"] == team_a]["Runs"].sum())
    team_b_runs = int(batting[batting["Batting_Team"] == team_b]["Runs"].sum())
    
    return {
        "Total_Matches": len(matches),
        f"{team_a}_Wins": team_a_wins,
        f"{team_b}_Wins": team_b_wins,
        f"{team_a}_Runs": team_a_runs,
        f"{team_b}_Runs": team_b_runs
    }


def runs_per_year(df: pd.DataFrame, team: str, format_: Optional[str] = None) -> pd.DataFrame:
    mask = (df["Batting_Team"] == team) & df["Runs"].notna()
    if format_:
        mask &= df["Format"] == format_
        
    batting_df = df[mask].copy()
    if batting_df.empty:
        return pd.DataFrame()
        
    # Extract year from Match_Date (which should be datetime)
    # If not datetime, fallback to string slicing
    if pd.api.types.is_datetime64_any_dtype(batting_df["Match_Date"]):
        batting_df["Year"] = batting_df["Match_Date"].dt.year
    else:
        batting_df["Year"] = batting_df["Match_Date"].str[:4].astype(int)
        
    yearly = batting_df.groupby("Year")["Runs"].sum().reset_index()
    yearly.columns = ["Year", "Total_Runs"]
    return yearly.sort_values("Year")
