import pandas as pd


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

    def filter_data(self, filters):
        # Takes the values of the 4 filter controls and uses pandas to select, where, etc...
        # This operation is always applied on the original data
        return self.vids_df  # TODO: implement

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

        return channels_df

    def summarize_data(self, df, which='videos'):
        # Gets means, variances, min, max, etc. for a given df's numeric variables
        # Which should be either 'videos', 'channels' or 'single' (stats for a single channel)

        # NOTE: df.groupby().describe() might be useful here
        # https://pandas.pydata.org/docs/user_guide/groupby.html

        return None  # TODO: implement

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
