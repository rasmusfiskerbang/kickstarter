from database.clean_data_frame import clean_data_frame
import pandas as pd
import numpy as np


def get_all_data(links_list: list, use_data_file: bool = True) -> pd.DataFrame:
    if not use_data_file:
        # Creating empty initial data frame
        data_full = pd.DataFrame()
        n_rows = list()

        for i in range(len(links_list)):
            # Downloading data frames
            data_small = clean_data_frame(links_list[i])

            # Concatenating data frames
            data_full = pd.concat([data_full, data_small], sort=False)

            # Dropping duplicates
            data_full = data_full.drop_duplicates(['name', 'created_at'])
    else:
        date_vars = ["created_at", "launched_at", "deadline", "state_changed_at"]
        data_full = pd.read_csv('database/full_data.csv', low_memory=False, parse_dates=date_vars)
    return data_full


def transform_numbers(data_full: pd.DataFrame) -> pd.DataFrame:
    # Getting fx_rate for each currency and date
    fx_rate_data: pd.DataFrame = data_full.copy()
    fx_rate_data = fx_rate_data.groupby(['currency', 'created_at', 'fx_rate']).size() \
        .reset_index().rename(columns={0: 'count'})

    # Setting all USD fx_rates equal to 1
    fx_rate_data.loc[fx_rate_data['currency'] == 'USD', 'fx_rate'] = 1

    # Setting fx_rate equal to the most common rate
    fx_rate_data = fx_rate_data.groupby(['currency', 'created_at']) \
        .apply(lambda x: x.sort_values('count', ascending=False).iloc[0, :]) \
        .reset_index(drop=True)

    # Creating data frame of wanted dates
    min_date = data_full.copy().groupby('currency').apply(lambda x: x.created_at.min())
    max_date = data_full.copy().groupby('currency').apply(lambda x: x.created_at.max())

    data_full_dates = pd.DataFrame(dict(created_at_min=min_date, created_at_max=max_date)).reset_index() \
        .groupby('currency').apply(lambda x: pd.date_range(x.created_at_min.iloc[0], x.created_at_max.iloc[0])) \
        .apply(lambda x: x.to_frame())

    data_full_dates_list = list()
    for data, index in zip(data_full_dates, data_full_dates.index):
        data_full_dates_list.append(data.assign(currency=index).reset_index(drop=True))
    data_full_dates: pd.DataFrame = pd.concat(data_full_dates_list).rename(columns={0: 'created_at'})

    # Merging wanted and actual dates
    fx_rate_data = data_full_dates.merge(fx_rate_data, 'left')

    # Sanity check
    fx_rate_data.loc[fx_rate_data['fx_rate'] > 2, 'fx_rate'] = np.nan

    # Filling missing values
    fx_rate_data.fx_rate = fx_rate_data.groupby('currency')['fx_rate'].ffill()
    fx_rate_data = fx_rate_data.drop('count', axis=1)

    # Merging with data full
    data_full = data_full.drop('fx_rate', axis=1)
    data_full = data_full.merge(fx_rate_data, 'left')

    # transforming goal and pledged with new fx_rate
    data_full.pledged = data_full.fx_rate * data_full.pledged
    data_full.goal = data_full.fx_rate * data_full.goal
    return data_full


def get_all(links: list) -> pd.DataFrame:
    # Getting all data
    data_full = get_all_data(links)

    # Transforming numbers
    data_full = transform_numbers(data_full)

    # Keeping necessary variables
    vars_keep = ["name", "backers_count", "state", "category", "sub_category", "creator",
                 "blurb", "country", "city", "created_at", "launched_at", "deadline",
                 "state_changed_at", "pledged", "goal", "spotlight", "staff_pick"]
    data_full = data_full[vars_keep]
    return data_full
