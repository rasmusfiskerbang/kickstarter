from database.link_handler import link_to_data_frame
import pandas as pd
import math
import re
import numpy as np
from datetime import datetime

# Vars to remove
vars_remove = ["converted_pledged_amount", "currency_symbol", "currency_trailing_code",
               "current_currency", "disable_communication", "friends", "id", "is_backing", "is_starrable",
               "is_starred", "permissions", "photo", "profile", "slug", "source", "urls", "usd_pledged", "usd_type",
               "static_usd_rate", "location", "source_url"]

date_vars = ["created_at", "launched_at", "deadline", "state_changed_at"]


def remove_vars(data_frame_input: pd.DataFrame) -> pd.DataFrame:
    vars_remove_actual = [column for column in data_frame_input.columns if column in vars_remove]
    data_frame_removed = data_frame_input.drop(vars_remove_actual, axis=1)
    return data_frame_removed


def extract_key_from_json(json_input: str, key) -> str:
    if isinstance(json_input, dict):
        return json_input[key]
    elif isinstance(json_input, float):
        if math.isnan(json_input):
            return None
    json_input = re.sub('^{', '', json_input)
    json_input = re.sub('}$', '', json_input)
    json_input = json_input.split(',')
    cond_key = np.array(['"' + key + '":' in json_small for json_small in json_input])
    pos_key = np.where(cond_key)[0][0]
    json_input = json_input[pos_key].split(':')[-1]
    json_input = re.sub('^"|"$', '', json_input)
    return json_input


def extract_category(df_input: pd.DataFrame) -> pd.DataFrame:
    category = df_input.category.apply(lambda x: extract_key_from_json(x, 'slug'))
    category_df = pd.DataFrame(category.str.split('/').tolist(), columns=['category', 'sub_category'])
    category_df = category_df.applymap(lambda x: None if x is None else str.title(x))
    df_input = df_input.drop('category', axis=1)
    df_output = pd.concat([df_input, category_df], 1)
    return df_output


def to_date_string(input_date: int):
    return datetime.utcfromtimestamp(input_date).replace(hour=0, minute=0, second=0, microsecond=0)


def clean_data_frame(link_input: str) -> pd.DataFrame:
    # Converting link to data frame
    data: pd.DataFrame = link_to_data_frame(link_input)

    # Resetting index
    data = data.reset_index()
    data = data.drop('index', 1)

    # Making data copy
    data_out = data.copy()

    # Extracting category
    data_out = extract_category(data_out) if 'category' in data_out.columns else data_out

    # Extracting creator
    if 'creator' in data_out.columns:
        data_out.creator = data_out.creator.apply(lambda x: extract_key_from_json(x, 'name'))

    # Extracting location
    if 'location' in data_out.columns:
        data_out['city'] = data_out.location.apply(lambda x: extract_key_from_json(x, 'name'))

    # Fixing dates
    date_vars_actual = [column for column in data_out.columns if column in date_vars]
    if len(date_vars_actual) > 0:
        data_out[date_vars_actual] = data_out[date_vars_actual].applymap(to_date_string)

    # Removing variables
    data_out = remove_vars(data_out)
    return data_out
