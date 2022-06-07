import json
from datetime import date

from dateutil import parser

from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px

import pandas as pd

from datascripts.pipeline import YTDataset
from components.controls.bubbleVars import BubbleVarsControl
from components.controls.filters import FiltersControl

# Constants
DATA_PATH = '..\\data\\USvideos_table.csv'

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

yt_dataset = YTDataset(DATA_PATH)
# TODO: might have to delete this line once filter callbacks are implemented
_, channels_df = yt_dataset.get_tables(filters={})

# App components
## Controls
### Filters
filters_control = FiltersControl(yt_dataset.vids_df, channels_df).controls

### Bubble plot variables
bubble_vars_control = BubbleVarsControl(channels_df).controls

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
                            dcc.Graph(id='channels-plot')
                        ])
                    ]),
                    dbc.Row([
                        html.H3("Good Mythical Morning's Videos"),
                        dcc.Graph()
                    ])
                ]),
                md=8),
            dbc.Col([
                html.H3("Statistics"),
                dbc.Label("TODO: summarization table goes here!", id='dummy-label'),
                html.Hr(),

                dbc.Accordion([
                    dbc.AccordionItem([filters_control], title="Filters"),
                    dbc.AccordionItem([bubble_vars_control], title="Bubble plot variables"),
                ], always_open=True)],
                md=4)
        ],
        align='Center'
    ),

    # dcc.Store for storing channels and vids table after filtering
    dcc.Store(id='tables-storage')
],
    fluid=True
)


# Callback definitions
@app.callback(
    Output('tables-storage', 'data'),
    Input('channel-category', 'value'),
    Input('vid-category', 'value'),
    Input('subs-range', 'value'),
    Input('views-range', 'value'),
    Input('trending-date-range', 'start_date'),
    Input('trending-date-range', 'end_date'),
)
def filter_tables(channel_cat,
                  video_cat,
                  subs_range,
                  views_range,
                  start_date, end_date):
    #print(channel_cat, video_cat, subs_range, start_date, end_date)

    filters = {
        # Videos df col  :  filter values
        'channel_category': channel_cat,
        'video_category': video_cat,
        'subscribers': tuple(subs_range),
        'views': tuple(views_range),
        'last_trending_date': (parser.parse(start_date), parser.parse(end_date))
    }

    filtered_vids, filtered_channels = yt_dataset.get_tables(filters=filters)

    dataframes = {
        'filtered_vids': filtered_vids.to_json(orient='split', date_format='iso'),
        'filtered_channels': filtered_channels.to_json(orient='split', date_format='iso'),
    }

    return json.dumps(dataframes)


@app.callback(
    Output('channels-plot', 'figure'),
    Input('tables-storage', 'data'),  # Also trigger after tables are updated in dcc.Store (browser memory)
    Input('bubble-x-axis', 'value'),
    Input('x-scale-radio', 'value'),
    Input('bubble-y-axis', 'value'),
    Input('y-scale-radio', 'value'),
    Input('bubble-color', 'value'),
    Input('bubble-size', 'value'))
def update_bubble_plot(dataframes,
                       x_axis_var, x_axis_scale,
                       y_axis_var, y_axis_scale,
                       color_var,
                       size_var):

    dataframes = json.loads(dataframes)
    filtered_channels_df = pd.read_json(dataframes['filtered_channels'], orient='split')

    figure = px.scatter(filtered_channels_df,
                        x=x_axis_var, y=y_axis_var,
                        color=color_var,
                        size=size_var,
                        hover_name='channel'
                        )

    figure.update_xaxes(title=x_axis_var, type=x_axis_scale)
    figure.update_yaxes(title=y_axis_var, type=y_axis_scale)

    return figure


if __name__ == '__main__':
    app.run_server(debug=True)
