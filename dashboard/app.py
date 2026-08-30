import dash
import dash_bootstrap_components as dbc
from dash import Dash, html
from flask import jsonify
import pandas as pd
import numpy as np

from dashboard.components.navbar import create_navbar
from data.loader import load_dataset

from analytics.player.stats import (
    batting_career,
    bowling_career,
    batting_history,
    bowling_history,
    top_run_scorers,
    top_wicket_takers,
    batting_form,
)

from analytics.team.stats import (
    win_loss_record,
    team_batting_summary,
    team_bowling_summary,
    head_to_head,
    runs_per_year,
)

from analytics.match.stats import (
    match_scorecard,
    highest_team_totals,
    venue_summary,
    matches_per_year,
)


# ============================================================
# DASH APPLICATION
# ============================================================

app = Dash(
    __name__,
    use_pages=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
)

app.title = "Cricket Research Lab"
server = app.server


# ============================================================
# CORS
# ============================================================

@server.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
    return response


# ============================================================
# JSON CLEANER
# ============================================================

def _clean_json(obj):
    if isinstance(obj, np.integer):
        return int(obj)

    if isinstance(obj, np.floating):
        return None if np.isnan(obj) else float(obj)

    if isinstance(obj, (float,)):
        return None if np.isnan(obj) else obj

    if isinstance(obj, pd.Timestamp):
        return obj.strftime("%Y-%m-%d")

    if isinstance(obj, dict):
        return {k: _clean_json(v) for k, v in obj.items()}

    if isinstance(obj, list):
        return [_clean_json(v) for v in obj]

    if obj is pd.NA:
        return None

    return obj


# ============================================================
# MATCH-LEVEL HELPERS
# ============================================================

def _match_potm(match_df):
    """
    Return the Player-of-the-Match recipient(s) for one match.

    Player_of_the_Match is intentionally populated only on the
    recipient's player-level row(s), so never obtain POTM by
    taking the first row of a match.
    """

    if "Player_of_the_Match" not in match_df.columns:
        return ""

    potm = (
        match_df["Player_of_the_Match"]
        .dropna()
        .astype(str)
        .str.strip()
    )

    potm = potm[potm != ""]

    if potm.empty:
        return ""

    # Preserve multiple recipients if present.
    recipients = list(dict.fromkeys(potm.tolist()))

    return ", ".join(recipients)


def _match_result(match_df):
    """Return the first non-blank match result."""
    if "Result" not in match_df.columns:
        return ""

    results = (
        match_df["Result"]
        .dropna()
        .astype(str)
        .str.strip()
    )

    results = results[results != ""]

    return results.iloc[0] if not results.empty else ""


def _match_metadata(match_df):
    """Return stable match metadata from the first row."""
    if match_df.empty:
        return {}

    row = match_df.iloc[0]

    return {
        "id": str(row["Match_ID"]),
        "date": (
            pd.to_datetime(row["Match_Date"]).strftime("%d %b %Y").upper()
            if pd.notna(row["Match_Date"])
            else ""
        ),
        "title": f"{row['Team_1']} vs {row['Team_2']}",
        "team1": str(row["Team_1"]),
        "team2": str(row["Team_2"]),
        "venue": str(row["Venue"]),
        "format": str(row["Format"]),
        "result": _match_result(match_df),
        "potm": _match_potm(match_df),
    }


# ============================================================
# API — OBSERVATORY
# ============================================================

@server.route("/api/observatory", methods=["GET"])
def get_observatory():

    df = load_dataset()

    # --------------------------------------------------------
    # Recent Matches
    # --------------------------------------------------------

    match_ids = (
        df[["Match_ID", "Match_Date"]]
        .drop_duplicates(subset=["Match_ID"])
        .sort_values("Match_Date", ascending=False)
        .head(10)["Match_ID"]
        .tolist()
    )

    recent_matches = []

    for match_id in match_ids:

        match_df = df[
            df["Match_ID"].astype(str) == str(match_id)
        ]

        meta = _match_metadata(match_df)

        recent_matches.append({
            "id": meta["id"],
            "date": meta["date"],
            "match": meta["title"],
            "result": meta["result"] or "Match Concluded",
            "impact": meta["potm"] or "N/A",
            "venue": meta["venue"],
            "format": meta["format"],
        })

    # --------------------------------------------------------
    # Top Players Form Index
    # --------------------------------------------------------

    top_scorers_df = top_run_scorers(df, top_n=5)

    top_players = []

    if not top_scorers_df.empty:

        for idx, row in top_scorers_df.reset_index().iterrows():

            form_df = batting_form(
                df,
                row["Player"],
                last_n=5,
            )

            trend = "up"

            if len(form_df) >= 2:

                last_two = form_df["Runs"].tail(2).tolist()

                if last_two[-1] < last_two[-2]:
                    trend = "down"

                elif last_two[-1] == last_two[-2]:
                    trend = "neutral"

            top_players.append({
                "rank": f"{idx + 1:02d}",
                "name": str(row["Player"]),
                "trend": trend,
                "runs": int(row["Runs"]),
                "average": float(row["Strike_Rate"]),
            })

    # --------------------------------------------------------
    # Global Metrics
    # --------------------------------------------------------

    total_matches = int(df["Match_ID"].nunique())
    total_runs = int(df["Runs"].sum())
    total_wickets = int(df["Wickets"].sum())
    venues_count = int(df["Venue"].nunique())

    return jsonify(
        _clean_json({
            "recentMatches": recent_matches,
            "topPlayers": top_players,
            "metrics": {
                "totalMatches": total_matches,
                "totalRuns": total_runs,
                "totalWickets": total_wickets,
                "venuesCount": venues_count,
            },
        })
    )


# ============================================================
# API — PLAYERS
# ============================================================

@server.route("/api/players", methods=["GET"])
def get_players():

    df = load_dataset()

    players = sorted(
        [
            str(p)
            for p in df["Player"].dropna().unique()
            if str(p).strip()
        ]
    )

    return jsonify(players)


# ============================================================
# API — PLAYER DETAILS
# ============================================================

@server.route("/api/player/<player_name>", methods=["GET"])
def get_player(player_name):

    df = load_dataset()

    player_df = df[df["Player"] == player_name]

    if player_df.empty:
        return jsonify({
            "error": f"Player '{player_name}' not found"
        }), 404

    bat_stats = batting_career(df, player_name)
    bowl_stats = bowling_career(df, player_name)

    teams = list(
        set(
            player_df["Batting_Team"].dropna().tolist()
            +
            player_df["Bowling_Team"].dropna().tolist()
        )
    )

    teams = [str(t) for t in teams if str(t).strip()]

    team_name = teams[0] if teams else "International"

    role = (
        player_df["Role"].iloc[0]
        if "Role" in player_df.columns
        and player_df["Role"].iloc[0]
        else "Top Order Batter"
    )

    # --------------------------------------------------------
    # Batting History
    # --------------------------------------------------------

    history_df = batting_history(df, player_name)

    innings = []

    if not history_df.empty:

        for _, row in history_df.iterrows():

            runs = int(row["Runs"])

            if runs >= 100:
                status = "century"
            elif runs >= 50:
                status = "fifty"
            elif runs == 0:
                status = "duck"
            else:
                status = "normal"

            innings.append({
                "score": runs,
                "status": status,
                "balls": (
                    int(row["Balls"])
                    if pd.notna(row["Balls"])
                    else 0
                ),
                "opponent": str(row["Bowling_Team"]),
            })

    # --------------------------------------------------------
    # Trajectory
    # --------------------------------------------------------

    trajectory = []

    if not history_df.empty:

        cumulative_runs = 0

        for i, runs in enumerate(
            history_df["Runs"].tolist(),
            1,
        ):

            cumulative_runs += int(runs)

            trajectory.append({
                "inning": i,
                "average": round(
                    cumulative_runs / i,
                    2,
                ),
            })

    # --------------------------------------------------------
    # Venue Summary
    # --------------------------------------------------------

    venue_rows = []

    batting_only = player_df[
        player_df["Runs"].notna()
    ]

    for venue, vgroup in batting_only.groupby("Venue"):

        v_inns = len(vgroup)
        v_runs = int(vgroup["Runs"].sum())

        v_avg = (
            round(v_runs / v_inns, 2)
            if v_inns > 0
            else 0.0
        )

        venue_rows.append({
            "condition": str(venue),
            "inns": v_inns,
            "runs": v_runs,
            "avg": v_avg,
        })

    venue_rows = sorted(
        venue_rows,
        key=lambda x: x["runs"],
        reverse=True,
    )[:5]

    # --------------------------------------------------------
    # Innings Split
    # --------------------------------------------------------

    first_second = player_df[
        player_df["Innings"].isin([1, 2])
        & player_df["Runs"].notna()
    ]

    third_fourth = player_df[
        player_df["Innings"].isin([3, 4])
        & player_df["Runs"].notna()
    ]

    first_second_runs = (
        int(first_second["Runs"].sum())
        if not first_second.empty
        else 0
    )

    third_fourth_runs = (
        int(third_fourth["Runs"].sum())
        if not third_fourth.empty
        else 0
    )

    first_second_avg = (
        round(
            first_second_runs / len(first_second),
            2,
        )
        if len(first_second) > 0
        else 0.0
    )

    third_fourth_avg = (
        round(
            third_fourth_runs / len(third_fourth),
            2,
        )
        if len(third_fourth) > 0
        else 0.0
    )

    return jsonify(
        _clean_json({
            "player": player_name,
            "team": team_name,
            "role": role,
            "batting": bat_stats,
            "bowling": bowl_stats,
            "innings": innings,
            "trajectory": trajectory,
            "venues": venue_rows,
            "inningsSplit": [
                {
                    "innings": "1st/2nd",
                    "inns": len(first_second),
                    "runs": first_second_runs,
                    "avg": first_second_avg,
                },
                {
                    "innings": "3rd/4th",
                    "inns": len(third_fourth),
                    "runs": third_fourth_runs,
                    "avg": third_fourth_avg,
                },
            ],
        })
    )


# ============================================================
# API — TEAMS
# ============================================================

@server.route("/api/teams", methods=["GET"])
def get_teams():

    df = load_dataset()

    teams = sorted(
        list(
            set(
                df["Team_1"].dropna().tolist()
                +
                df["Team_2"].dropna().tolist()
            )
        )
    )

    teams = [
        str(team)
        for team in teams
        if str(team).strip()
    ]

    return jsonify(teams)


# ============================================================
# API — TEAM DETAILS
# ============================================================

@server.route("/api/team/<team_name>", methods=["GET"])
def get_team(team_name):

    df = load_dataset()

    team_matches = df[
        (df["Team_1"] == team_name)
        |
        (df["Team_2"] == team_name)
    ].drop_duplicates(
        subset=["Match_ID"]
    ).sort_values("Match_Date")

    if team_matches.empty:
        return jsonify({
            "error": f"Team '{team_name}' not found"
        }), 404

    momentum = []

    for _, row in team_matches.iterrows():

        result = str(row["Result"])

        if result == f"{team_name} won":
            momentum.append("W")

        elif "won" in result:
            momentum.append("L")

        else:
            momentum.append("D")

    bat_summary = team_batting_summary(
        df,
        team_name,
    )

    bowl_summary = team_bowling_summary(
        df,
        team_name,
    )

    squad = []

    if not bat_summary.empty:

        for idx, row in bat_summary.head(8).iterrows():

            avg_val = (
                round(
                    row["Runs"] / row["Innings"],
                    1,
                )
                if row["Innings"] > 0
                else 0.0
            )

            squad.append({
                "name": str(row["Player"]),
                "role": "BAT",
                "stat": str(avg_val),
                "leader": idx == 0,
            })

    if not bowl_summary.empty:

        for idx, row in bowl_summary.head(6).iterrows():

            if not any(
                p["name"] == str(row["Player"])
                for p in squad
            ):

                squad.append({
                    "name": str(row["Player"]),
                    "role": "BOWL",
                    "stat": str(row["Average"]),
                    "leader": idx == 0,
                })

    all_teams = sorted(
        list(
            set(
                df["Team_1"].dropna().tolist()
                +
                df["Team_2"].dropna().tolist()
            )
        )
    )

    h2h_list = []

    for opponent in all_teams:

        if opponent and opponent != team_name:

            record = head_to_head(
                df,
                team_name,
                opponent,
            )

            if (
                record
                and record.get("Total_Matches", 0) > 0
            ):

                total = record["Total_Matches"]

                wins = record[
                    f"{team_name}_Wins"
                ]

                losses = record[
                    f"{opponent}_Wins"
                ]

                draws = total - wins - losses

                win_pct = (
                    round(
                        (wins / total) * 100,
                        1,
                    )
                    if total > 0
                    else 0.0
                )

                h2h_list.append({
                    "team": opponent,
                    "win": int(win_pct),
                    "draw": draws,
                    "loss": losses,
                    "wins_count": wins,
                })

    h2h_list = sorted(
        h2h_list,
        key=lambda x: (
            x["wins_count"]
            +
            x["loss"]
            +
            x["draw"]
        ),
        reverse=True,
    )

    return jsonify(
        _clean_json({
            "team": team_name,
            "ranking": (
                f"International Squad "
                f"({len(team_matches)} Matches)"
            ),
            "momentum": momentum,
            "squad": squad,
            "h2h": h2h_list,
        })
    )


# ============================================================
# API — MATCH LIST
# ============================================================

@server.route("/api/matches", methods=["GET"])
def get_matches():

    df = load_dataset()

    match_ids = (
        df[["Match_ID", "Match_Date"]]
        .drop_duplicates(subset=["Match_ID"])
        .sort_values("Match_Date", ascending=False)
        ["Match_ID"]
        .tolist()
    )

    matches = []

    for match_id in match_ids:

        match_df = df[
            df["Match_ID"].astype(str)
            == str(match_id)
        ]

        meta = _match_metadata(match_df)

        matches.append({
            "id": meta["id"],
            "date": meta["date"],
            "title": meta["title"],
            "venue": meta["venue"],
            "result": (
                meta["result"]
                or "Match Concluded"
            ),
            "format": meta["format"],
            "potm": meta["potm"] or "N/A",
        })

    return jsonify(
        _clean_json(matches)
    )


# ============================================================
# API — SINGLE MATCH SCORECARD
# ============================================================

@server.route("/api/match/<match_id>", methods=["GET"])
def get_match(match_id):

    df = load_dataset()

    match_df = df[
        df["Match_ID"].astype(str)
        == str(match_id)
    ].copy()

    if match_df.empty:
        return jsonify({
            "error": f"Match '{match_id}' not found"
        }), 404

    sc = match_scorecard(
        df,
        match_id,
    )

    if not sc or not sc.get("Metadata"):
        return jsonify({
            "error": f"Match '{match_id}' not found"
        }), 404

    meta = sc["Metadata"]

    # --------------------------------------------------------
    # IMPORTANT:
    # Get POTM from the complete match DataFrame.
    # Do NOT use the first row.
    # --------------------------------------------------------

    potm = _match_potm(match_df)

    innings_raw = sc.get(
        "Innings",
        [],
    )

    innings_list = []

    for inn in innings_raw:

        batting_rows = []

        for _, brow in inn["Batting"].iterrows():

            runs = (
                int(brow["Runs"])
                if pd.notna(brow["Runs"])
                else 0
            )

            balls = (
                int(brow["Balls"])
                if pd.notna(brow["Balls"])
                else 0
            )

            fours = (
                int(brow["4s"])
                if pd.notna(brow["4s"])
                else 0
            )

            sixes = (
                int(brow["6s"])
                if pd.notna(brow["6s"])
                else 0
            )

            sr = (
                str(round(
                    brow["Strike_Rate"],
                    2,
                ))
                if pd.notna(brow["Strike_Rate"])
                else "0.0"
            )

            batting_rows.append({
                "bat": str(brow["Player"]),
                "dismissal": "b / c",
                "runs": runs,
                "balls": balls,
                "fours": fours,
                "sixes": sixes,
                "sr": sr,
            })

        # ----------------------------------------------------
        # Partnership approximation
        # ----------------------------------------------------

        partnerships = []

        if len(batting_rows) >= 2:

            max_runs = max(
                [b["runs"] for b in batting_rows]
            )

            for i in range(
                len(batting_rows) - 1
            ):

                partnership_runs = (
                    batting_rows[i]["runs"]
                    +
                    batting_rows[i + 1]["runs"]
                )

                percentage = min(
                    100,
                    max(
                        15,
                        int(
                            (
                                partnership_runs
                                /
                                (max_runs * 2 or 1)
                            )
                            * 100
                        ),
                    ),
                )

                partnerships.append({
                    "players": (
                        f"{batting_rows[i]['bat'].split()[-1]}"
                        f" & "
                        f"{batting_rows[i + 1]['bat'].split()[-1]}"
                    ),
                    "runs": partnership_runs,
                    "height": f"{percentage}%",
                })

        innings_list.append({
            "inning": inn["Inning"],
            "battingTeam": inn["Totals"]["Batting_Team"],
            "bowlingTeam": inn["Totals"]["Bowling_Team"],
            "totalRuns": inn["Totals"]["Total_Runs"],
            "wickets": inn["Totals"]["Wickets_Fallen"],
            "scorecard": batting_rows,
            "partnerships": partnerships[:5],
        })

    match_date = (
        pd.to_datetime(
            meta["Match_Date"]
        ).strftime("%d %b %Y").upper()
        if pd.notna(meta["Match_Date"])
        else ""
    )

    return jsonify(
        _clean_json({
            "id": str(meta["Match_ID"]),
            "teams": (
                f"{meta['Team_1']} "
                f"v "
                f"{meta['Team_2']}"
            ),
            "team1": meta["Team_1"],
            "team2": meta["Team_2"],
            "venue": meta["Venue"],
            "date": match_date,
            "format": meta["Format"],
            "result": (
                _match_result(match_df)
                or "Match Concluded"
            ),
            "potm": potm,
            "innings": innings_list,
        })
    )


# ============================================================
# DASH LAYOUT
# ============================================================

app.layout = html.Div(
    [
        create_navbar(),

        dbc.Container(
            dash.page_container,
            fluid=True,
            className="p-4",
        ),
    ],
    className="app-container",
)


# ============================================================
# START BACKEND
# ============================================================

if __name__ == "__main__":
    app.run(
        debug=True,
        host="127.0.0.1",
        port=8050,
    )