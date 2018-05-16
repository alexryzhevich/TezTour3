import pandas as pd
import numpy as np

from core.config import initial_grid as init_config, layout as layout_config, parameters as param_config
from core.layout.layout import Layout
from core.layout.util import read_excel, get_layout_col, get_required_col
from exceptions.exceptions import WRONG_EXCEL_FORMAT_ERROR, LAYOUT_NAME_FORMAT_ERROR, NO_ROWS_REQUESTED_ERROR


def generate_layout(initial_data_filename, min_days, max_days, duration_limit, relations, width, name, id):
    initial_data = read_excel(initial_data_filename)
    # layout = pd.DataFrame()
    try:
        layout = _get_layout_data_from_file(initial_data, name)
        # layout[layout_config.IN_DATES_COL] = initial_data[init_config.IN_DATES_COL]
        # layout[layout_config.IN_PLACES_COL] = initial_data[init_config.IN_PLACES_COL]
        for i in range(width):
            layout = layout.assign(**{get_layout_col(i): layout[layout_config.IN_PLACES_COL].apply(lambda _: None)})
        # layout[layout_config.OUT_PLACES_COL] = initial_data[init_config.OUT_PLACES_COL]
        # layout[layout_config.OUT_DATES_COL] = initial_data[init_config.OUT_DATES_COL]
        for i in range(width):
            layout = layout.assign(**{get_required_col(i): layout[layout_config.IN_PLACES_COL].apply(lambda _: False)})
        date_relations = [None for _ in layout[layout_config.IN_DATES_COL]]
        out_of_order = [[] for _ in layout[layout_config.IN_DATES_COL]]
        no_losses = [[False, False] for _ in layout[layout_config.IN_DATES_COL]]
    except KeyError:
        raise WRONG_EXCEL_FORMAT_ERROR

    layout_obj = Layout(name, layout, date_relations, out_of_order, None, no_losses, duration_limit=duration_limit,
                        width=width, max_days=max_days, min_days=min_days, relations=relations, id=id)

    return layout_obj


def _get_layout_data_from_file(initial_data: pd.DataFrame, name: str):
    from_name, to_name = _get_airport_names(name)

    initial_data[init_config.IN_DATES_COL] = initial_data[init_config.IN_DATES_COL]\
        .apply(lambda x: x.replace(hour=0, minute=0, second=0))
    initial_data[init_config.OUT_DATES_COL] = initial_data[init_config.OUT_DATES_COL]\
        .apply(lambda x: x.replace(hour=0, minute=0, second=0))

    in_data = initial_data[[init_config.IN_PLACES_COL, init_config.IN_DATES_COL,
                            init_config.IN_AIRPORT_FROM, init_config.IN_AIRPORT_TO]]
    in_data = in_data[in_data[init_config.IN_AIRPORT_FROM].str.contains(from_name, case=False)
                      & in_data[init_config.IN_AIRPORT_TO].str.contains(to_name, case=False)].groupby(
        init_config.IN_DATES_COL)[init_config.IN_PLACES_COL].sum().reset_index()

    out_data = initial_data[[init_config.OUT_PLACES_COL, init_config.OUT_DATES_COL,
                            init_config.OUT_AIRPORT_FROM, init_config.OUT_AIRPORT_TO]]
    out_data = out_data[out_data[init_config.OUT_AIRPORT_FROM].str.contains(to_name, case=False)
                        & out_data[init_config.OUT_AIRPORT_TO].str.contains(from_name, case=False)].groupby(
        init_config.OUT_DATES_COL)[init_config.OUT_PLACES_COL].sum().reset_index()

    if in_data.shape[0] == 0 or out_data.shape[0] == 0:
        raise NO_ROWS_REQUESTED_ERROR

    full_data = pd.concat([pd.DataFrame(columns=[layout_config.IN_DATES_COL, layout_config.OUT_DATES_COL],
                                        dtype='datetime64[ns]'),
                           pd.DataFrame(columns=[layout_config.IN_PLACES_COL, layout_config.OUT_PLACES_COL],
                                        dtype=float)], axis=1)
    in_idx, out_idx = 0, 0
    while in_idx < in_data.shape[0] or out_idx < out_data.shape[0]:
        if out_idx < out_data.shape[0] \
                and (in_idx >= in_data.shape[0]
                     or out_data[init_config.OUT_DATES_COL][out_idx] < in_data[init_config.IN_DATES_COL][in_idx]):
            full_data = full_data.append({layout_config.OUT_PLACES_COL: out_data[init_config.OUT_PLACES_COL][out_idx],
                                          layout_config.OUT_DATES_COL: out_data[init_config.OUT_DATES_COL][out_idx],
                                          layout_config.IN_DATES_COL: pd.NaT},
                                         ignore_index=True)
            out_idx += 1
            continue
        if in_idx < in_data.shape[0] \
                and (out_idx >= out_data.shape[0]
                     or in_data[init_config.IN_DATES_COL][in_idx] < out_data[init_config.OUT_DATES_COL][out_idx]):
            full_data = full_data.append({layout_config.IN_PLACES_COL: in_data[init_config.IN_PLACES_COL][in_idx],
                                          layout_config.IN_DATES_COL: in_data[init_config.IN_DATES_COL][in_idx],
                                          layout_config.OUT_DATES_COL: pd.NaT},
                                         ignore_index=True)
            in_idx += 1
            continue
        full_data = full_data.append({layout_config.OUT_PLACES_COL: out_data[init_config.OUT_PLACES_COL][out_idx],
                                      layout_config.OUT_DATES_COL: out_data[init_config.OUT_DATES_COL][out_idx],
                                      layout_config.IN_PLACES_COL: in_data[init_config.IN_PLACES_COL][in_idx],
                                      layout_config.IN_DATES_COL: in_data[init_config.IN_DATES_COL][in_idx]},
                                     ignore_index=True)
        in_idx += 1
        out_idx += 1
    return full_data


def _get_airport_names(name: str):
    names = name.split(layout_config.AIRPORT_NAMES_SEPARATOR)
    if len(names) != 2:
        raise LAYOUT_NAME_FORMAT_ERROR
    from_name, to_name = names[0].strip(), names[1].strip()
    if len(from_name) == 0 or len(to_name) == 0:
        raise LAYOUT_NAME_FORMAT_ERROR
    return from_name, to_name


def _fill_empty_layout(layout, width):
    height = layout[layout_config.IN_PLACES_COL].shape[0]
    current_idx = 0
    for i in range(height):
        max_places = layout[layout_config.IN_PLACES_COL][i]
        #layout[get_layout_col(current_idx)][i] = max_places
        for j in range(i, min(i + param_config.MAX_DAYS + 1, height)):
            delta = (layout[layout_config.OUT_DATES_COL][j] - layout[layout_config.IN_DATES_COL][i]).days
            if np.isnan(delta) or delta < param_config.MIN_DAYS:
                continue
            if delta > param_config.MAX_DAYS:
                break
            layout[get_layout_col(current_idx)][j] = 5
            break
        current_idx = (current_idx + 1) % width
