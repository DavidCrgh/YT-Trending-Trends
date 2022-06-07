import json
from datetime import date

from dateutil import parser

from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
from plotly.subplots import make_subplots

import pandas as pd

from datascripts.pipeline import YTDataset
from components.controls.bubbleVars import BubbleVarsControl
from components.controls.filters import FiltersControl
from components.controls.timeseriesVars import TimeSeriesControl

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

### Timeseries plot variables
timeseries_vars_control = TimeSeriesControl(yt_dataset.vids_df).controls

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
                        html.H3("Channel Videos", id='channel-plot-header'),
                        dcc.Graph(id='videos-plot')
                    ])
                ]),
                md=8, lg=8),
            dbc.Col([
                html.H3("Statistics"),
                dbc.Label("TODO: summarization table goes here!", id='dummy-label'),
                html.Hr(),

                dbc.Accordion([
                    dbc.AccordionItem([filters_control], title="Filters"),
                    dbc.AccordionItem([bubble_vars_control], title="Bubble plot variables"),
                    dbc.AccordionItem([timeseries_vars_control], title='Timeseries variables')
                ], always_open=True)],
                md=4, lg=4)
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
    # print(channel_cat, video_cat, subs_range, start_date, end_date)

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
                        hover_name='channel',
                        size_max=25
                        )

    figure.update_xaxes(title=x_axis_var, type=x_axis_scale)
    figure.update_yaxes(title=y_axis_var, type=y_axis_scale)

    return figure


@app.callback(
    Output('videos-plot', 'figure'),
    Output('channel-plot-header', 'children'),
    Input('channels-plot', 'clickData'),
    Input('timeseries-y-var', 'value'),
    Input('tables-storage', 'data'))
def update_timeseries(clickData, y_axis_var, dataframes):
    dataframes = json.loads(dataframes)
    filtered_vids_df = pd.read_json(dataframes['filtered_vids'], orient='split')
    filtered_vids_df = filtered_vids_df.sort_values(by=['last_trending_date'])

    channel = filtered_vids_df.channel.mode().iloc[0]  # Get most repeated channel

    # If selection exists and is valid, overwrite channel
    if clickData is not None:
        selected_channel = clickData['points'][0]['hovertext']

        if selected_channel in filtered_vids_df['channel'].values:
            channel = selected_channel

    filtered_vids_df = filtered_vids_df[filtered_vids_df['channel'] == channel]  # Select only channel's vids

    figure = px.scatter(filtered_vids_df, x='last_trending_date', y=y_axis_var, hover_name='title')
    figure.update_traces(mode='lines+markers')

    return figure, f'{channel} Trending Videos'


if __name__ == '__main__':
    app.run_server(debug=True)
