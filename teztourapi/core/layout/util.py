import pandas as pd

from core.config import initial_grid as init_config, layout as layout_config, parameters as param_config
from exceptions.exceptions import WRONG_FILE_FORMAT_ERROR

DATE_FORMAT = '%Y-%m-%d'


def read_excel(filename):
    try:
        return pd.read_excel(filename)
    except:
        raise WRONG_FILE_FORMAT_ERROR


def save_to_excel(data, filename='output.xlsx', sheetname='Sheet1'):
    writer = pd.ExcelWriter(filename)
    data.to_excel(writer, sheetname)


def get_layout_col(idx):
    return layout_config.LAYOUT_COL + str(idx + 1)


def get_required_col(idx):
    return layout_config.REQUIRED_COL + str(idx + 1)


def calculate_layout_width(duration_limit=param_config.DURATION_LIMIT):
    return max(layout_config.MIN_WIDTH, duration_limit + layout_config.MIN_DISTANCE_BETWEEN_ROWS)


def ts_to_str(ts):
    return ts.strftime(DATE_FORMAT) if not pd.isnull(ts) else None


def fl_to_int(fl):
    return int(fl) if not pd.isnull(fl) else None


def str_to_ts(s):
    return None if s is None else pd.Timestamp(s)
