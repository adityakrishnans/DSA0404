import pandas as pd
from typing import Optional, Dict


def batting_career(df: pd.DataFrame, player: str, format_: Optional[str] = None) -> Dict:
    mask = df["Player"] == player
    if format_:
        mask &= df["Format"] == format_
        
    player_df = df[mask]
    
    # Empty state handling
    if player_df.empty:
        return {}

    # Filter to actual batting innings (where Runs is not null)
    batting_df = player_df[player_df["Runs"].notna()]
    
    matches = player_df["Match_ID"].nunique()
    innings = len(batting_df)
    
    if innings == 0:
        return {}

    runs = int(batting_df["Runs"].sum())
    balls = int(batting_df["Balls"].sum())
    fours = int(batting_df["4s"].sum())
    sixes = int(batting_df["6s"].sum())
    
    highest = int(batting_df["Runs"].max()) if not batting_df.empty else 0
    hundreds = int((batting_df["Runs"] >= 100).sum())
    fifties = int(((batting_df["Runs"] >= 50) & (batting_df["Runs"] < 100)).sum())
    
    # Note: Traditional batting average considers dismissals, but our dataset records 
    # player_out as part of deliveries but doesn't easily indicate "not out" at the innings level
    # in the 26 columns. For Version 1.0, average is Runs / Innings.
    average = round(runs / innings, 2) if innings > 0 else 0.0
    strike_rate = round((runs / balls) * 100, 2) if balls > 0 else 0.0

    return {
        "Matches": matches,
        "Innings": innings,
        "Runs": runs,
        "Balls": balls,
        "4s": fours,
        "6s": sixes,
        "Average": average,
        "Strike_Rate": strike_rate,
        "Highest": highest,
        "100s": hundreds,
        "50s": fifties
    }


def bowling_career(df: pd.DataFrame, player: str, format_: Optional[str] = None) -> Dict:
    mask = df["Player"] == player
    if format_:
        mask &= df["Format"] == format_
        
    player_df = df[mask]
    
    if player_df.empty:
        return {}

    # Filter to actual bowling innings
    bowling_df = player_df[player_df["Overs"].notna()]
    
    matches = player_df["Match_ID"].nunique()
    innings = len(bowling_df)
    
    if innings == 0:
        return {}

    overs = int(bowling_df["Overs"].sum())
    maidens = int(bowling_df["Maidens"].sum())
    runs_conceded = int(bowling_df["Runs_Conceded"].sum())
    wickets = int(bowling_df["Wickets"].sum())
    
    average = round(runs_conceded / wickets, 2) if wickets > 0 else 0.0
    economy = round(runs_conceded / overs, 2) if overs > 0 else 0.0
    
    # Best figures
    if not bowling_df.empty:
        best_spell = bowling_df.sort_values(by=["Wickets", "Runs_Conceded"], ascending=[False, True]).iloc[0]
        best_figures = f"{int(best_spell['Wickets'])}-{int(best_spell['Runs_Conceded'])}"
    else:
        best_figures = "0-0"
        
    # Strike rate (Balls / Wickets). We approximate balls as overs * 6 since we dropped exact balls for economy.
    balls_bowled = overs * 6
    strike_rate = round(balls_bowled / wickets, 2) if wickets > 0 else 0.0

    return {
        "Matches": matches,
        "Innings": innings,
        "Overs": overs,
        "Maidens": maidens,
        "Runs_Conceded": runs_conceded,
        "Wickets": wickets,
        "Average": average,
        "Economy": economy,
        "Strike_Rate": strike_rate,
        "Best_Figures": best_figures
    }


def batting_history(df: pd.DataFrame, player: str, format_: Optional[str] = None) -> pd.DataFrame:
    mask = (df["Player"] == player) & df["Runs"].notna()
    if format_:
        mask &= df["Format"] == format_
        
    history = df[mask].copy()
    if history.empty:
        return pd.DataFrame()
        
    history = history.sort_values("Match_Date")
    return history[["Match_ID", "Match_Date", "Format", "Batting_Team", "Bowling_Team", 
                    "Innings", "Batting_Position", "Runs", "Balls", "4s", "6s", "Strike_Rate"]]


def bowling_history(df: pd.DataFrame, player: str, format_: Optional[str] = None) -> pd.DataFrame:
    mask = (df["Player"] == player) & df["Overs"].notna()
    if format_:
        mask &= df["Format"] == format_
        
    history = df[mask].copy()
    if history.empty:
        return pd.DataFrame()
        
    history = history.sort_values("Match_Date")
    return history[["Match_ID", "Match_Date", "Format", "Batting_Team", "Bowling_Team", 
                    "Innings", "Overs", "Maidens", "Runs_Conceded", "Wickets", "Economy"]]


def top_run_scorers(df: pd.DataFrame, format_: Optional[str] = None, top_n: int = 10) -> pd.DataFrame:
    mask = df["Runs"].notna()
    if format_:
        mask &= df["Format"] == format_
        
    batting_df = df[mask]
    if batting_df.empty:
        return pd.DataFrame()
        
    # Deduplicate match counts correctly
    match_counts = batting_df.drop_duplicates(subset=["Match_ID", "Player"]).groupby("Player").size().rename("Matches")
    
    grouped = batting_df.groupby("Player").agg(
        Innings=("Runs", "count"),
        Runs=("Runs", "sum"),
        Balls=("Balls", "sum"),
        Highest=("Runs", "max")
    )
    
    grouped["100s"] = batting_df[batting_df["Runs"] >= 100].groupby("Player").size()
    grouped["50s"] = batting_df[(batting_df["Runs"] >= 50) & (batting_df["Runs"] < 100)].groupby("Player").size()
    
    grouped = grouped.fillna(0)
    grouped = grouped.join(match_counts).reset_index()
    
    grouped["Strike_Rate"] = (grouped["Runs"] / grouped["Balls"] * 100).round(2).fillna(0)
    
    top = grouped.sort_values("Runs", ascending=False).head(top_n)
    
    # Cast ints back to standard ints or Int64
    for col in ["Matches", "Innings", "Runs", "Balls", "Highest", "100s", "50s"]:
        top[col] = top[col].astype("Int64")
        
    return top[["Player", "Matches", "Innings", "Runs", "Balls", "100s", "50s", "Highest", "Strike_Rate"]]


def top_wicket_takers(df: pd.DataFrame, format_: Optional[str] = None, top_n: int = 10) -> pd.DataFrame:
    mask = df["Overs"].notna()
    if format_:
        mask &= df["Format"] == format_
        
    bowling_df = df[mask]
    if bowling_df.empty:
        return pd.DataFrame()
        
    match_counts = bowling_df.drop_duplicates(subset=["Match_ID", "Player"]).groupby("Player").size().rename("Matches")
    
    grouped = bowling_df.groupby("Player").agg(
        Innings=("Overs", "count"),
        Wickets=("Wickets", "sum"),
        Runs_Conceded=("Runs_Conceded", "sum"),
        Overs=("Overs", "sum")
    )
    
    grouped = grouped.join(match_counts).reset_index()
    
    grouped["Average"] = (grouped["Runs_Conceded"] / grouped["Wickets"]).round(2)
    grouped["Economy"] = (grouped["Runs_Conceded"] / grouped["Overs"]).round(2)
    
    top = grouped.sort_values("Wickets", ascending=False).head(top_n)
    
    for col in ["Matches", "Innings", "Wickets", "Runs_Conceded", "Overs"]:
        top[col] = top[col].astype("Int64")
        
    return top[["Player", "Matches", "Innings", "Wickets", "Runs_Conceded", "Overs", "Average", "Economy"]]


def player_of_match_count(df: pd.DataFrame, format_: Optional[str] = None, top_n: int = 10) -> pd.DataFrame:
    mask = df["Player_of_the_Match"] != ""
    if format_:
        mask &= df["Format"] == format_
        
    awards_df = df[mask].drop_duplicates(subset=["Match_ID"])
    if awards_df.empty:
        return pd.DataFrame()
        
    counts = awards_df["Player_of_the_Match"].value_counts().reset_index()
    counts.columns = ["Player", "Awards"]
    
    return counts.head(top_n)


def batting_form(df: pd.DataFrame, player: str, format_: Optional[str] = None, last_n: int = 10) -> pd.DataFrame:
    history = batting_history(df, player, format_)
    if history.empty:
        return pd.DataFrame()
        
    recent = history.tail(last_n).copy()
    recent["Rolling_Avg"] = recent["Runs"].expanding().mean().round(2)
    
    return recent
