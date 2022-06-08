import pandas as pd

from src.utils.util_scripts import format_var_names

class YTDataset:
    def __init__(self, path):
        self.path = path
        self.vids_df = None
        self.init_df(path)

    def get_tables(self, filters):
        # Calls the pipeline process to convert a table of videos to a table of channels
        filtered_df = self.filter_data(filters)
        channels_df = self.aggregate_channels(filtered_df)

        return filtered_df, channels_df

    def filter_data(self, filters: dict):
        # Takes the values of the 4 filter controls and uses pandas to select, where, etc...
        # This operation is always applied on the original data
        df = self.vids_df

        for column, value in filters.items():
            if type(value) is list and value != []:
                df = df[df[column].isin(value)]
            elif type(value) is tuple:
                df = df[df[column].between(value[0], value[1])]

        return df

    def aggregate_channels(self, df):
        # Takes a YTDataset df, groups by channels, and aggregates (avg, counts, etc.)

        channels_df = df.groupby(['channel'], as_index=False).agg(
            channel_category=('channel_category', 'first'),
            subscribers=('subscribers', 'max'),
            times_in_trending=('video_id', 'count'),
            avg_views=('views', 'mean'),
            avg_likes=('likes', 'mean'),
            avg_dislikes=('dislikes', 'mean'),
            avg_comment_count=('comment_count', 'mean'),
            avg_tags_in_title=('tags_in_title', 'mean'),
            avg_days_trending=('days_in_trending', 'mean'),
            avg_days_to_trending=('days_to_trending', 'mean'),
            avg_tags_count=('tags_count', 'mean'),
        )

        channels_df = channels_df.dropna()  # NaN values are present if filtering was applied, no idea why

        return channels_df

    def summarize_data(self, df):
        # Gets means, variances, min, max, etc. for a given df's numeric variables

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

        return stats

    def init_df(self, path):
        df = pd.read_csv(path)

        # Parse as datetime columns
        df['last_trending_date'] = pd.to_datetime(df['last_trending_date'])
        df['publish_date'] = pd.to_datetime(df['publish_date'])

        # Define categorical variables
        df = df.astype({'channel': 'category',
                        'channel_category': 'category',
                        'video_category': 'category'})

        self.vids_df = df
