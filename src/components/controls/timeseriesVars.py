import numpy as np
import pandas as pd

from dash import dcc, html
import dash_bootstrap_components as dbc

from src.utils.util_scripts import map_vars_list


class TimeSeriesControl:
    def __init__(self, vids_df: pd.DataFrame, default_y_one='views'):
        self.default_y_one = default_y_one
        self.data = vids_df
        self.controls = None
        self.init_controls()

    def init_controls(self):
        numeric_vars = list(self.data.select_dtypes(include=[np.number]))

        controls = dbc.Container([
            html.Div([
                dbc.Label("Y axis"),
                dcc.Dropdown(
                    id="timeseries-y-var",
                    options=map_vars_list(numeric_vars),
                    value=self.default_y_one
                )
            ])
        ])
        self.controls = controls
