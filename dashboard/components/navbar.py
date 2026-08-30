import dash_bootstrap_components as dbc
from dash import html

def create_navbar():
    return dbc.NavbarSimple(
        children=[
            dbc.NavItem(dbc.NavLink("Home", href="/", active="exact")),
            dbc.NavItem(dbc.NavLink("Player Profile", href="/player", active="exact")),
            dbc.NavItem(dbc.NavLink("Team Profile", href="/team", active="exact")),
            dbc.NavItem(dbc.NavLink("Match Analysis", href="/match", active="exact")),
        ],
        brand="Cricket Research Lab",
        brand_href="/",
        color="primary",
        dark=True,
        className="navbar-custom mb-4",
    )
