import numpy as np
import pandas as pd

from dash import dcc, html
import dash_bootstrap_components as dbc


class BubbleVarsControl:
    def __init__(self,
                 channels_df: pd.DataFrame,
                 default_x='times_in_trending',
                 default_y='avg_views',
                 default_color_var='channel_category',
                 default_size_var='subscribers'):

        self.default_x = default_x
        self.default_y = default_y
        self.default_color_var = default_color_var
        self.default_size_var = default_size_var

        self.data = channels_df
        self.controls = None
        self.init_controls()

    def init_controls(self):
        numeric_vars = list(self.data.select_dtypes(include=[np.number]))

        controls = dbc.Container([
            html.Div([
                dbc.Label("X axis"),
                dcc.Dropdown(
                    id='bubble-x-axis',
                    options=numeric_vars,
                    value=self.default_x
                ),
                dbc.RadioItems(
                    options=[
                        {"label": "Linear", "value": 'linear'},
                        {"label": "Log", "value": 'log'},
                    ],
                    value='linear',
                    id="x-scale-radio",
                    inline=True,
                ),
            ]),
            html.Div([
                dbc.Label("Y axis"),
                dcc.Dropdown(
                    id="bubble-y-axis",
                    options=numeric_vars,
                    value=self.default_y
                ),
                dbc.RadioItems(
                    options=[
                        {"label": "Linear", "value": 'linear'},
                        {"label": "Log", "value": 'log'},
                    ],
                    value='linear',
                    id="y-scale-radio",
                    inline=True,
                ),
            ]),
            html.Div([
                dbc.Label("Color"),
                dcc.Dropdown(
                    id="bubble-color",
                    options=['channel_category'] + numeric_vars,
                    value=self.default_color_var
                )
            ]),
            html.Div([
                dbc.Label("Bubble size"),
                dcc.Dropdown(
                    id="bubble-size",
                    options=numeric_vars,
                    value=self.default_size_var
                )
            ]),
        ])

        self.controls = controls
