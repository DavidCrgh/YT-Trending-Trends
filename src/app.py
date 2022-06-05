import os

from datascripts.pipeline import YTDataset

# Constants
DATA_PATH = 'data\\USvideos_table.csv'

yt_data = YTDataset(DATA_PATH)

mydf = yt_data.aggregate_channels(yt_data.df)
