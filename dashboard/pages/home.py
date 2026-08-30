import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd

from data.loader import load_dataset
from dashboard.components.cards import kpi_card
from analytics.player.stats import top_run_scorers, top_wicket_takers, player_of_match_count

dash.register_page(__name__, path="/", name="Home", order=0)

# We use load_dataset directly to pass to analytics functions.
try:
    df = load_dataset()
    available_formats = sorted([f for f in df["Format"].unique() if f])
    
    # Pre-calculate global aggregates for initial load without format filter
    total_matches = df["Match_ID"].nunique()
    total_runs = int(df["Runs"].sum()) if not df.empty else 0
    total_wickets = int(df[df["Overs"].notna()]["Wickets"].sum()) if not df.empty else 0
except Exception as e:
    df = pd.DataFrame()
    available_formats = []
    total_matches = total_runs = total_wickets = 0


layout = html.Div([
    html.H2("Dashboard Overview", className="mb-4 text-primary"),
    
    dbc.Row([
        dbc.Col(kpi_card("Total Matches", f"{total_matches:,}"), width=4),
        dbc.Col(kpi_card("Total Runs Scored", f"{total_runs:,}"), width=4),
        dbc.Col(kpi_card("Total Wickets Fallen", f"{total_wickets:,}"), width=4),
    ], className="mb-4"),
    
    dbc.Row([
        dbc.Col([
            html.H5("Format Filter", className="text-muted"),
            dcc.Dropdown(
                id="home-format-filter",
                options=[{"label": f, "value": f} for f in available_formats],
                value=None,
                placeholder="All Formats"
            )
        ], width=4)
    ], className="mb-4"),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Top Run Scorers"),
                dbc.CardBody(dcc.Graph(id="home-top-scorers"))
            ])
        ], width=6),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Top Wicket Takers"),
                dbc.CardBody(dcc.Graph(id="home-top-wickets"))
            ])
        ], width=6)
    ], className="mb-4"),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Player of the Match Awards"),
                dbc.CardBody(dcc.Graph(id="home-potm"))
            ])
        ], width=12)
    ])
])

@callback(
    Output("home-top-scorers", "figure"),
    Output("home-top-wickets", "figure"),
    Output("home-potm", "figure"),
    Input("home-format-filter", "value")
)
def update_home_charts(selected_format):
    if df.empty:
        return {}, {}, {}
        
    # Get analytics
    runs_df = top_run_scorers(df, format_=selected_format, top_n=10)
    wkts_df = top_wicket_takers(df, format_=selected_format, top_n=10)
    potm_df = player_of_match_count(df, format_=selected_format, top_n=10)
    
    # Common chart aesthetics (no grid on Y)
    def style_fig(fig):
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            yaxis=dict(showgrid=False),
            xaxis=dict(showgrid=False),
            margin=dict(l=20, r=20, t=40, b=20)
        )
        return fig
        
    # Build charts
    if not runs_df.empty:
        fig_runs = px.bar(runs_df, x="Player", y="Runs", title="Top Runs", color_discrete_sequence=["#0074D9"])
        fig_runs = style_fig(fig_runs)
    else:
        fig_runs = {}
        
    if not wkts_df.empty:
        fig_wkts = px.bar(wkts_df, x="Player", y="Wickets", title="Top Wickets", color_discrete_sequence=["#2ECC40"])
        fig_wkts = style_fig(fig_wkts)
    else:
        fig_wkts = {}
        
    if not potm_df.empty:
        fig_potm = px.bar(potm_df, x="Player", y="Awards", title="POTM Awards", color_discrete_sequence=["#FF851B"])
        fig_potm = style_fig(fig_potm)
    else:
        fig_potm = {}
        
    return fig_runs, fig_wkts, fig_potm
