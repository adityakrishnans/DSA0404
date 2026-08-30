import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd

from data.loader import load_dataset
from dashboard.components.cards import kpi_card
from analytics.team.stats import win_loss_record, runs_per_year

dash.register_page(__name__, path="/team", name="Team Profile", order=2)

try:
    df = load_dataset()
    # Safely derive unique teams directly from the dataframe
    if not df.empty:
        all_teams = pd.concat([df["Team_1"], df["Team_2"]]).unique()
        teams = sorted([t for t in all_teams if t])
        formats = sorted([f for f in df["Format"].unique() if f])
    else:
        teams = []
        formats = []
except Exception:
    df = pd.DataFrame()
    teams = []
    formats = []

layout = html.Div([
    html.H2("Team Profile", className="mb-4 text-primary"),
    
    dbc.Row([
        dbc.Col([
            dcc.Dropdown(
                id="team-select",
                options=[{"label": t, "value": t} for t in teams],
                value=teams[0] if teams else None,
                placeholder="Select a Team"
            )
        ], width=4),
        dbc.Col([
            dcc.Dropdown(
                id="team-format-filter",
                options=[{"label": f, "value": f} for f in formats],
                value=None,
                placeholder="All Formats"
            )
        ], width=4)
    ], className="mb-4"),
    
    html.Div(id="team-win-loss-kpis", className="mb-4"),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Runs Scored Per Year"),
                dbc.CardBody(dcc.Graph(id="team-runs-chart"))
            ])
        ], width=12)
    ])
])

@callback(
    Output("team-win-loss-kpis", "children"),
    Output("team-runs-chart", "figure"),
    Input("team-select", "value"),
    Input("team-format-filter", "value")
)
def update_team_profile(team, format_):
    if not team or df.empty:
        return "", {}
        
    wl = win_loss_record(df, team, format_)
    runs = runs_per_year(df, team, format_)
    
    if wl:
        kpis = dbc.Row([
            dbc.Col(kpi_card("Matches", str(wl.get("Total_Matches", 0)))),
            dbc.Col(kpi_card("Wins", str(wl.get("Wins", 0)))),
            dbc.Col(kpi_card("Losses", str(wl.get("Losses", 0)))),
            dbc.Col(kpi_card("Win %", str(wl.get("Win_Percentage", 0)))),
        ])
    else:
        kpis = html.P("No records found.", className="text-muted")
        
    if not runs.empty:
        fig = px.bar(runs, x="Year", y="Total_Runs", title=f"{team} Runs per Year", color_discrete_sequence=["#2ECC40"])
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            yaxis=dict(showgrid=False),
            xaxis=dict(showgrid=False, type='category'),
            margin=dict(l=20, r=20, t=40, b=20)
        )
    else:
        fig = {}
        
    return kpis, fig
