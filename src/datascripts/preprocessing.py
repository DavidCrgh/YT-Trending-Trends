import pandas as pd

RAW_VIDS_PATH = '..\\..\\data\\raw\\USvideos_modified.csv'
CHANNEL_CATS_PATH = '..\\..\\data\\raw\\Trending CrowdSourced Classification.csv'
VIDEO_CATS_PATH = '..\\..\\data\\raw\\video_cats.csv'

OUT_CSV_PATH = '..\\..\\data\\USvideos_table.csv'

# Run this script to transform the files in data/raw/ into a single CSV
raw_videos = pd.read_csv(RAW_VIDS_PATH)
channel_cats = pd.read_csv(CHANNEL_CATS_PATH)
video_cats = pd.read_csv(VIDEO_CATS_PATH)

# Step 1 - Select only the columns we'll probably need
# Dropping tags and description also reduces required space
videos_df = raw_videos.drop(columns=['publish_hour',
                                     'tags',
                                     'description',
                                     'trend_tag_highest',
                                     'trend_tag_total'])


# Step 2 - Match channel titles with their crowdsourced category
videos_df = pd.merge(videos_df,
                      channel_cats[['channel', 'classification']],
                      how='left',
                      left_on='channel_title',
                      right_on='channel'
                      )
videos_df = videos_df.drop(columns=['channel'])

# Step 3 - Match video category ID with their category string
videos_df = pd.merge(videos_df,
                     video_cats,
                     on='category_id',
                     how='left')
videos_df = videos_df.drop(columns=['category_id']) # We no longer need this column


# Step 4 - Replace nan or null values
videos_df['subscriber'] = videos_df['subscriber'].fillna(0)
videos_df['classification'] = videos_df['classification'].fillna('UC') # UC for 'unclassified'

# Step 5 - Rename columns and save to CSV
videos_df = videos_df.rename(columns={
    'channel_title': 'channel',
    'tag_appeared_in_title_count': 'tags_in_title',
    'trend_day_count': 'days_in_trending',
    'trend.publish.diff': 'days_to_trending',
    'subscriber': 'subscribers',
    'classification': 'channel_category',
    'category': 'video_category'
})
# Change subs from float to int
videos_df = videos_df.astype({'subscribers': 'int64'})

videos_df.to_csv(OUT_CSV_PATH, index=False)
