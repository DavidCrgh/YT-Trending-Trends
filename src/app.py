import json

import pandas as pd
import plotly.express as px

from dateutil import parser

from dash import Dash, dcc, html, Input, Output
from dash.dash_table import DataTable
from dash.dash_table.Format import Format, Scheme
import dash_bootstrap_components as dbc

from datascripts.pipeline import YTDataset
from components.controls.bubbleVars import BubbleVarsControl
from components.controls.filters import FiltersControl
from components.controls.timeseriesVars import TimeSeriesControl

from src.utils.util_scripts import format_var_names

# Constants
DATA_PATH = '..\\data\\USvideos_table.csv'

app = Dash(__name__, external_stylesheets=[dbc.themes.JOURNAL])

yt_dataset = YTDataset(DATA_PATH)
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
    dbc.Row([
        # TODO: move the styling here to a CSS file
        html.H1("YouTube Trending & Trends (T&T)",
                style={'color': '#EB6864', 'margin-top': '10px', 'margin-bottom': '15px'}),
        html.Hr(style={'margin-bottom': '0px'}),
    ], style={'background-color': '#FDF0F0', 'margin-bottom': '20px'}),
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
                dbc.RadioItems(
                    options=[
                        {"label": "Channels", "value": 'channels'},
                        {"label": "Videos", "value": 'vids'},
                    ],
                    value='channels',
                    id="stats-table",
                    inline=True,
                ),
                html.Div(id="summary-table-div"),
                html.Hr(),

                dbc.Accordion([
                    dbc.AccordionItem([filters_control], title="Filters"),
                    dbc.AccordionItem([bubble_vars_control], title="Bubble plot variables"),
                    dbc.AccordionItem([timeseries_vars_control], title='Timeseries variables')
                ], always_open=False)],
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
                        size_max=25,
                        labels={
                            x_axis_var: format_var_names(x_axis_var),
                            y_axis_var: format_var_names(y_axis_var),
                            color_var: format_var_names(color_var),
                            size_var: format_var_names(size_var)
                        })

    figure.update_xaxes(type=x_axis_scale)
    figure.update_yaxes(type=y_axis_scale)

    return figure


@app.callback(
    Output('videos-plot', 'figure'),
    Output('channel-plot-header', 'children'),
    Input('channels-plot', 'clickData'),
    Input('timeseries-y-var', 'value'),
    Input('tables-storage', 'data'))
def update_timeseries(clickData, y_axis_var, dataframes):
    x_axis_var = 'last_trending_date'

    dataframes = json.loads(dataframes)
    filtered_vids_df = pd.read_json(dataframes['filtered_vids'], orient='split')
    filtered_vids_df = filtered_vids_df.sort_values(by=[x_axis_var])

    channel = filtered_vids_df.channel.mode().iloc[0]  # Get most repeated channel


    # If selection exists and is valid, overwrite channel
    if clickData is not None:
        selected_channel = clickData['points'][0]['hovertext']

        if selected_channel in filtered_vids_df['channel'].values:
            channel = selected_channel

    filtered_vids_df = filtered_vids_df[filtered_vids_df['channel'] == channel]  # Select only channel's vids

    figure = px.scatter(filtered_vids_df,
                        x=x_axis_var,
                        y=y_axis_var,
                        color_discrete_sequence=px.colors.qualitative.Pastel1,
                        hover_name='title',
                        labels={
                            x_axis_var: format_var_names(x_axis_var),
                            y_axis_var: format_var_names(y_axis_var)
                        })
    figure.update_traces(mode='lines+markers')

    return figure, f'{channel} Trending Videos'


@app.callback(
    Output('summary-table-div', 'children'),
    Input('stats-table', 'value'),
    Input('tables-storage', 'data')
)
def update_summary_table(selected_table, dataframes):
    dataframes = json.loads(dataframes)
    df = pd.read_json(dataframes['filtered_' + selected_table], orient='split')

    stats = df.describe().transpose()[['mean', 'std', 'min', '50%', 'max']]
    stats = stats.rename_axis('Variable').reset_index()  # Include row names as a column to display it
    stats['Variable'] = stats.apply(
        lambda row: format_var_names(row['Variable']),
        axis=1)
    stats = stats.rename(columns={'mean': 'Mean',
                                  'std': 'SD',
                                  '50%': 'Median',
                                  'min': 'Min',
                                  'max': 'Max'})

    table = DataTable(
        data=stats.to_dict('records'),
        columns=[{"name": i,
                  "id": i,
                  "type": "numeric",
                  "format": Format(precision=2, scheme=Scheme.decimal_si_prefix)
                  } for i in stats.columns],
        style_cell_conditional=[
            {
                'if': {'column_id': c},
                'textAlign': 'left'
            } for c in stats.columns
        ],
        style_table={'overflowX': 'auto'},  # Horizontal scrolling
        style_as_list_view=True
    )

    return table


if __name__ == '__main__':
    app.run_server(debug=True)
