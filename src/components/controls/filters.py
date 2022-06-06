from datetime import date

import numpy as np
import pandas as pd

from dash import dcc, html
import dash_bootstrap_components as dbc

from src.utils.util_scripts import human_format


class FiltersControl:
    def __init__(self,
                 vids_df: pd.DataFrame,
                 channels_df: pd.DataFrame):

        self.vids_df = vids_df
        self.channels_df = channels_df

        self.controls = None
        self.init_controls()

    def init_controls(self):
        vid_categories = self.vids_df['video_category'].unique()
        channel_categories = self.vids_df['channel_category'].unique()

        controls = dbc.Container([
            html.Div([
                dbc.Label("Channel Category"),
                dbc.Checklist(
                    options=self.generate_check_options(channel_categories),
                    id='channel-category',
                    inline=True,
                    value=[]
                )
            ]),
            html.Hr(),
            html.Div([
                dbc.Label("Video category"),
                dbc.Checklist(
                    options=self.generate_check_options(vid_categories),
                    id='vid-category',
                    inline=True,
                    value=[]
                )
            ]),
            html.Hr(),
            html.Div([
                dbc.Label("Subscriber range"),
                self.generate_range_slider('subs-range', 'subscribers')
            ]),
            #html.Div([
             #   dbc.Label("Views range"),
              #  self.generate_range_slider('views-range', 'views')
            #]),
            #html.Div([
             #   dbc.Label("Comment count range"),
              #  self.generate_range_slider('comment-range', 'comment_count')
            #]),
            html.Hr(),
            html.Div([
                html.Div("Last trending date"),
                dcc.DatePickerRange(
                    id='trending-date-range',
                    min_date_allowed=self.vids_df['last_trending_date'].min(),
                    max_date_allowed=self.vids_df['last_trending_date'].max(),
                    start_date=self.vids_df['last_trending_date'].min(),
                    end_date=self.vids_df['last_trending_date'].max(),
                    initial_visible_month=date(2017, 8, 5),
                )
            ]),
        ])

        self.controls = controls

    def generate_check_options(self, options):
        checkitems = []

        for option in options:
            checkitems.append({'label': option, 'value': option})

        return checkitems

    def generate_range_slider(self, control_id, var_name):
        max_value = self.vids_df[var_name].max()

        slider = dcc.RangeSlider(
            0,
            max_value,
            allowCross=False,
            tooltip={"placement": "bottom", "always_visible": False},
            value=[0, max_value],
            id=control_id
        )

        return slider
