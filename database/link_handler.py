import requests
from zipfile import ZipFile
import io
import json
import pandas as pd


def download_zip_file(link_input: str) -> ZipFile:
    response = requests.get(link_input)
    return ZipFile(io.BytesIO(response.content))


def zip_to_json(link_input: str) -> list:
    file = download_zip_file(link_input)
    file_name = file.namelist()[0]
    data = file.open(file_name).read()
    string = data.decode('utf-8')
    string = string.replace('}\n{', '},{')
    json_out = json.loads(string)
    return json_out


def csv_to_data_frame(link_input: str) -> pd.DataFrame:
    zip_file = download_zip_file(link_input)
    data_frame_list = [pd.read_csv(zip_file.open(filename)) for filename in zip_file.infolist()]
    data_frame = pd.concat(data_frame_list)
    return data_frame


def json_to_data_frame(link_input: str) -> pd.DataFrame:
    data_frame_list = [pd.DataFrame(json_small['projects']) for json_small in zip_to_json(link_input)]
    data_frame = pd.concat(data_frame_list, sort=False)
    return data_frame


def link_to_data_frame(link_input: str) -> pd.DataFrame:
    if link_input.endswith('Z.zip'):
        return csv_to_data_frame(link_input)
    else:
        return json_to_data_frame(link_input)
