import time
import uuid
import numpy as np
import pandas as pd

from core.config.layout import IN_DATES_COL, IN_PLACES_COL, OUT_DATES_COL, OUT_PLACES_COL
import core.layout.layout as core_layout
from core.layout.util import get_layout_col, get_required_col
from exceptions.exceptions import LAYOUT_DATES_NOT_EQUAL_ERROR


def check_layouts_dates_equality(layout_obj1: core_layout.Layout, layout_obj2: core_layout.Layout):
    if layout_obj1.data[IN_DATES_COL].equals(layout_obj2.data[IN_DATES_COL]) \
            and layout_obj1.data[OUT_DATES_COL].equals(layout_obj2.data[OUT_DATES_COL]):
        return
    raise LAYOUT_DATES_NOT_EQUAL_ERROR


def update_out_of_order(layout_obj: core_layout.Layout, out_of_order: list):
    avail_out_places = [x for x in layout_obj.data[OUT_PLACES_COL]]
    avail_in_places = [x for x in layout_obj.data[IN_PLACES_COL]]
    for in_date, date_ooo in enumerate(out_of_order):
        for out_date, amount, _ in date_ooo:
            if avail_in_places[in_date] is None or avail_out_places[out_date] is None:
                continue
            new_amount = min([amount, avail_out_places[out_date], avail_in_places[in_date]])
            avail_out_places[out_date] -= new_amount
            avail_in_places[in_date] -= new_amount
            layout_obj.out_of_order[in_date].append((out_date, new_amount, new_amount < amount))


def update_required_fields(new_layout_obj: core_layout.Layout, old_layout_obj: core_layout.Layout):
    avail_in_places, avail_out_places = _calc_available_places(new_layout_obj)
    old_avail_in_places, old_avail_out_places = _calc_available_places(old_layout_obj)
    _update_required_fields_with_col_priorities(new_layout_obj, old_layout_obj, avail_in_places, avail_out_places,
                                                old_avail_in_places, old_avail_out_places)
    _update_required_fields_with_row_priorities(new_layout_obj, old_layout_obj, avail_out_places, old_avail_out_places)


def _calc_available_places(layout_obj: core_layout.Layout):
    avail_out_places = [int(x) if not pd.isnull(x) else None for x in layout_obj.data[OUT_PLACES_COL]]
    avail_in_places = [int(x) if not pd.isnull(x) else None for x in layout_obj.data[IN_PLACES_COL]]
    for in_date, date_ooo in enumerate(layout_obj.out_of_order):
        for out_date, amount, _ in date_ooo:
            if avail_in_places[in_date] is None or avail_out_places[out_date] is None:
                continue
            avail_out_places[out_date] -= amount
            avail_in_places[in_date] -= amount
    return avail_in_places, avail_out_places


def _update_required_fields_with_col_priorities(new_layout_obj: core_layout.Layout, old_layout_obj: core_layout.Layout,
                                                avail_in_places, avail_out_places, old_avail_in_places,
                                                old_avail_out_places):
    required_idxs = [[] for _ in range(old_layout_obj.width)]
    required_values = [[] for _ in range(old_layout_obj.width)]
    for i in range(old_layout_obj.data.shape[0]):
        if avail_in_places[i] is None or old_avail_in_places[i] is None or old_avail_in_places == 0:
            continue
        coef = avail_in_places[i] / old_avail_in_places[i]
        current_idx = i % old_layout_obj.width
        for j in range(i, min(i + old_layout_obj.max_days + 1, old_layout_obj.data.shape[0])):
            delta = (old_layout_obj.data[OUT_DATES_COL][j] - old_layout_obj.data[IN_DATES_COL][i]).days
            if np.isnan(delta) or delta < old_layout_obj.min_days:
                continue
            if delta > old_layout_obj.max_days:
                break
            if avail_out_places[j] is None or old_avail_out_places[j] is None:
                continue
            amount = old_layout_obj.data[get_layout_col(current_idx)][j]
            required = old_layout_obj.data[get_required_col(current_idx)][j]
            if required:
                new_amount = int(amount * coef)
                required_values[current_idx].append(new_amount)
                required_idxs[current_idx].append(j)
    for i in range(old_layout_obj.width):
        new_layout_obj.data[get_required_col(i)][required_idxs[i]] = True
        new_layout_obj.data[get_layout_col(i)][required_idxs[i]] = np.array(required_values[i])


def _update_required_fields_with_row_priorities(new_layout_obj: core_layout.Layout, old_layout_obj: core_layout.Layout,
                                                avail_out_places, old_avail_out_places):
    required_idxs = [[] for _ in range(old_layout_obj.width)]
    required_values = [[] for _ in range(old_layout_obj.width)]
    for i in range(old_layout_obj.data.shape[0]):
        if avail_out_places[i] is None or old_avail_out_places[i] == 0:
            continue
        col_idxs = []
        col_values = []
        new_col_values = []
        used_sum = 0
        for j in range(new_layout_obj.width):
            old_amount = old_layout_obj.data[get_layout_col(j)][i]
            new_amount = new_layout_obj.data[get_layout_col(j)][i]
            required = old_layout_obj.data[get_required_col(j)][i]
            if required:
                col_idxs.append(j)
                col_values.append(int(old_amount))
                new_col_values.append(int(new_amount))
                used_sum += int(new_amount)
        if used_sum <= avail_out_places[i]:
            continue
        coef = avail_out_places[i] / old_avail_out_places[i]
        for idx, old_value, new_value in zip(col_idxs, col_values, new_col_values):
            required_values[idx].append(min(int(old_value * coef), new_value))
            required_idxs[idx].append(i)
    for i in range(old_layout_obj.width):
        new_layout_obj.data[get_layout_col(i)][required_idxs[i]] = np.array(required_values[i])


def generate_unique_filename(filename: str):
    return str(time.time()) + '-' + filename


def generate_edit_token():
    return str(uuid.uuid4())
