import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd

from data.loader import load_dataset
from dashboard.components.cards import kpi_card
from analytics.player.stats import batting_career, bowling_career, batting_form, batting_history

dash.register_page(__name__, path="/player", name="Player Profile", order=1)

try:
    df = load_dataset()
    players = sorted([p for p in df["Player"].unique() if p])
    formats = sorted([f for f in df["Format"].unique() if f])
except Exception:
    df = pd.DataFrame()
    players = []
    formats = []

layout = html.Div([
    html.H2("Player Profile", className="mb-4 text-primary"),
    
    dbc.Row([
        dbc.Col([
            dcc.Dropdown(
                id="player-select",
                options=[{"label": p, "value": p} for p in players],
                value=players[0] if players else None,
                placeholder="Select a Player"
            )
        ], width=4),
        dbc.Col([
            dcc.Dropdown(
                id="player-format-filter",
                options=[{"label": f, "value": f} for f in formats],
                value=None,
                placeholder="All Formats"
            )
        ], width=4)
    ], className="mb-4"),
    
    html.H4("Batting Career", className="text-secondary"),
    html.Div(id="player-batting-kpis", className="mb-4"),
    
    html.H4("Bowling Career", className="text-secondary"),
    html.Div(id="player-bowling-kpis", className="mb-4"),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Batting Form (Last 10 Innings)"),
                dbc.CardBody(dcc.Graph(id="player-form-chart"))
            ])
        ], width=12)
    ])
])

@callback(
    Output("player-batting-kpis", "children"),
    Output("player-bowling-kpis", "children"),
    Output("player-form-chart", "figure"),
    Input("player-select", "value"),
    Input("player-format-filter", "value")
)
def update_player_profile(player, format_):
    if not player or df.empty:
        return "", "", {}
        
    batting = batting_career(df, player, format_)
    bowling = bowling_career(df, player, format_)
    form = batting_form(df, player, format_)
    
    # Batting KPIs
    if batting:
        bat_kpis = dbc.Row([
            dbc.Col(kpi_card("Matches", str(batting.get("Matches", 0)))),
            dbc.Col(kpi_card("Runs", str(batting.get("Runs", 0)))),
            dbc.Col(kpi_card("Average", str(batting.get("Average", 0)))),
            dbc.Col(kpi_card("Strike Rate", str(batting.get("Strike_Rate", 0)))),
            dbc.Col(kpi_card("Highest", str(batting.get("Highest", 0)))),
        ])
    else:
        bat_kpis = html.P("No batting records found.", className="text-muted")
        
    # Bowling KPIs
    if bowling:
        bowl_kpis = dbc.Row([
            dbc.Col(kpi_card("Wickets", str(bowling.get("Wickets", 0)))),
            dbc.Col(kpi_card("Average", str(bowling.get("Average", 0)))),
            dbc.Col(kpi_card("Economy", str(bowling.get("Economy", 0)))),
            dbc.Col(kpi_card("Best Figures", str(bowling.get("Best_Figures", "0-0")))),
        ])
    else:
        bowl_kpis = html.P("No bowling records found.", className="text-muted")
        
    # Form Chart
    if not form.empty:
        # Convert index to a string or generic sequence for the x-axis
        form["Inning_Seq"] = range(1, len(form) + 1)
        fig = px.line(form, x="Inning_Seq", y=["Runs", "Rolling_Avg"], 
                      title=f"{player} Form", color_discrete_sequence=["#0074D9", "#FF851B"])
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            yaxis=dict(showgrid=False),
            xaxis=dict(showgrid=False),
            margin=dict(l=20, r=20, t=40, b=20)
        )
    else:
        fig = {}
        
    return bat_kpis, bowl_kpis, fig
