from datetime import date

from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px

import pandas as pd

from datascripts.pipeline import YTDataset

# Constants
DATA_PATH = '..\\data\\USvideos_table.csv'

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

yt_dataset = YTDataset(DATA_PATH)
# TODO: might have to delete this line once filter callbacks are implemented
channels_df = yt_dataset.get_channels_table(filters=[])

# App components
## Controls
filters_control = dbc.Container([
    html.Div([
        dbc.Label("Channel Category"),
        dcc.Dropdown(
            id="channel-category",
            options=['Hello', 'world'],  # TODO: change for list of numerical vars
            value='Hello'
        )
    ]),
    html.Div([
        dbc.Label("Video category"),
        dcc.Dropdown(
            id="vid-category",
            options=['Hello', 'world'],  # TODO: change for list of numerical vars
            value='Hello'
        )
    ]),
    #html.Div([
     #   dbc.Label("Subscriber range"),
      #  dcc.RangeSlider(0, 20, 1, value=[0, 20], id='subs-range')
    #]),
    html.Div([
        html.Div("Publish date"),
        dcc.DatePickerRange(
            id='publish-date-range',
            min_date_allowed=date(1995, 8, 5),
            max_date_allowed=date(2017, 9, 19),
            initial_visible_month=date(2017, 8, 5),
        )
    ]),
])

bubble_vars_control = dbc.Container([
    #html.H4("Bubble plot variables", className="card-title"),
    #html.Hr(),

    html.Div([
        dbc.Label("X axis"),
        dcc.Dropdown(
            id='bubble-x-axis',
            options=['Hello', 'world'],  # TODO: change for list of numerical vars
            value='Hello'
        )
    ]),
    html.Div([
        dbc.Label("Y axis"),
        dcc.Dropdown(
            id="bubble-y-axis",
            options=['Hello', 'world'],  # TODO: change for list of numerical vars
            value='Hello'
        )
    ]),
    html.Div([
        dbc.Label("Color"),
        dcc.Dropdown(
            id="bubble-color",
            options=['Hello', 'world'],  # TODO: change for list of channel categories
            value='Hello'
        )
    ]),
    html.Div([
        dbc.Label("Bubble size"),
        dcc.Dropdown(
            id="bubble-size",
            options=['Hello', 'world'],  # TODO: change for list of numerical vars
            value='Hello'
        )
    ]),
])

# Main app layout declaration
app.layout = dbc.Container([
    html.H1("YouTube Trending & Trends (T&T)"),
    html.Hr(),

    dbc.Row(
        [
            dbc.Col(
                dbc.Container([
                    dbc.Row([
                        dbc.Col([
                            html.H3("Trending Channels"),
                            dcc.Graph()
                        ])
                    ]),
                    dbc.Row([
                        html.H3("Good Mythical Morning's Videos"),
                        dcc.Graph()
                    ])
                ]),
                md=8),
            dbc.Col([
                dbc.Label("Hello world!"),
                dbc.Accordion([
                    dbc.AccordionItem([filters_control], title="Filters"),
                    dbc.AccordionItem([bubble_vars_control], title="Bubble plot variables"),
                ], always_open=True)],
                md=4)
        ],
        align='Center'
    )],

    fluid=True
)

if __name__ == '__main__':
    app.run_server(debug=True)
