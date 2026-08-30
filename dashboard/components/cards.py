import dash_bootstrap_components as dbc
from dash import html

def kpi_card(title: str, value: str, icon: str = "") -> dbc.Card:
    """
    Creates a simple KPI card with no border, adhering to SDS guidelines.
    """
    return dbc.Card(
        dbc.CardBody(
            [
                html.H6(title, className="card-title text-muted"),
                html.H3(value, className="card-text text-primary"),
            ]
        ),
        className="text-center"
    )
