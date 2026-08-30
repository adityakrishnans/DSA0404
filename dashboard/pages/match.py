import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd

from data.loader import load_dataset
from dashboard.components.cards import kpi_card
from analytics.match.stats import highest_team_totals, venue_summary

dash.register_page(__name__, path="/match", name="Match Analysis", order=3)

try:
    df = load_dataset()
    if not df.empty:
        formats = sorted([f for f in df["Format"].unique() if f])
    else:
        formats = []
except Exception:
    df = pd.DataFrame()
    formats = []

layout = html.Div([
    html.H2("Match Analysis", className="mb-4 text-primary"),
    
    dbc.Row([
        dbc.Col([
            dcc.Dropdown(
                id="match-format-filter",
                options=[{"label": f, "value": f} for f in formats],
                value=None,
                placeholder="All Formats"
            )
        ], width=4)
    ], className="mb-4"),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Highest Team Totals"),
                dbc.CardBody(dcc.Graph(id="match-totals-chart"))
            ])
        ], width=6),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Venue Summaries (Matches Hosted)"),
                dbc.CardBody(dcc.Graph(id="match-venues-chart"))
            ])
        ], width=6)
    ])
])

@callback(
    Output("match-totals-chart", "figure"),
    Output("match-venues-chart", "figure"),
    Input("match-format-filter", "value")
)
def update_match_analysis(format_):
    if df.empty:
        return {}, {}
        
    totals = highest_team_totals(df, format_, top_n=10)
    venues = venue_summary(df, format_, top_n=10)
    
    def style_fig(fig):
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            yaxis=dict(showgrid=False),
            xaxis=dict(showgrid=False),
            margin=dict(l=20, r=20, t=40, b=20)
        )
        return fig
        
    if not totals.empty:
        # Create a string label combining team and date for the x-axis
        totals["Label"] = totals["Batting_Team"] + " (" + totals["Match_Date"].dt.strftime("%Y-%m-%d").astype(str) + ")"
        fig_totals = px.bar(totals, x="Label", y="Total_Runs", title="Highest Totals", color_discrete_sequence=["#FF851B"])
        fig_totals = style_fig(fig_totals)
    else:
        fig_totals = {}
        
    if not venues.empty:
        fig_venues = px.bar(venues, x="Venue", y="Matches", title="Matches by Venue", color_discrete_sequence=["#001f3f"])
        fig_venues = style_fig(fig_venues)
    else:
        fig_venues = {}
        
    return fig_totals, fig_venues
