import numpy as np
import pandas as pd

from core.layout.layout import Layout
from core.config import layout as layout_config
from core.layout.optimize.min_losses_step import min_losses_step
from core.layout.optimize.no_losses_step import no_losses_step
from core.layout.optimize.priority_step import priority_step
from core.layout.util import get_layout_col, get_required_col, DATE_FORMAT
from exceptions.exceptions import RESTRICTION_VIOLATION_ERROR_CODE, OOO_ILLEGAL_PLACE_ERROR_CODE
from exceptions.structs import ErrorMessage


def optimize(layout: Layout, last_update: str=None):
    _null_prev_day_values(layout, last_update)
    _check_ooo_durations(layout)
    avail_in_places = _get_avail_in_places(layout)
    avail_out_places = _get_avail_out_places(layout)
    corrected_relations, vars_num = _get_corrected_relations(layout)
    priority_step(layout, avail_in_places, avail_out_places, corrected_relations, vars_num)
    min_losses_step(layout, avail_in_places, avail_out_places, vars_num)
    no_losses_step(layout, avail_in_places, avail_out_places, corrected_relations)


def _null_prev_day_values(layout: Layout, last_update: str=None):
    null_by_date = pd.Timestamp.now() if last_update is None else pd.Timestamp.strptime(last_update, DATE_FORMAT)
    required_idxs = [[] for _ in range(layout.width)]
    for i in range(layout.data.shape[0]):
        if pd.isnull(layout.data[layout_config.IN_PLACES_COL][i]):
            continue
        current_idx = i % layout.width
        now_delta = (null_by_date - layout.data[layout_config.IN_DATES_COL][i]).days
        if now_delta <= 0:
            break
        for j in range(i, min(i + layout.max_days + 1, layout.data.shape[0])):
            delta = (layout.data[layout_config.OUT_DATES_COL][j] - layout.data[layout_config.IN_DATES_COL][i]).days
            if np.isnan(delta) or delta < layout.min_days:
                continue
            if delta > layout.max_days:
                break
            if pd.isnull(layout.data[layout_config.OUT_PLACES_COL][j]):
                continue
            required = layout.data[get_required_col(current_idx)][j]
            if not required:
                required_idxs[current_idx].append(j)
    for i in range(layout.width):
        layout.data[get_required_col(i)][required_idxs[i]] = True
        layout.data[get_layout_col(i)][required_idxs[i]] = 0


def _get_avail_out_places(layout):
    out_of_order = layout.out_of_order
    layout_data = layout.data
    height = layout_data.shape[0]
    width = layout.width
    out_of_order_places = [0] * height
    for data_list in out_of_order:
        for i, amount, _ in data_list:
            out_of_order_places[i] += amount
    out_places = []
    for i in range(height):
        cur_sum = 0
        for j in range(width):
            cur_idx = get_layout_col(j)
            cur_req_idx = get_required_col(j)
            if layout_data[cur_req_idx][i]:
                cur_sum += layout_data[cur_idx][i]
        cur_sum += out_of_order_places[i]
        out_max_places = layout_data[layout_config.OUT_PLACES_COL][i]
        if out_max_places is not None and cur_sum > out_max_places:
            raise ErrorMessage(RESTRICTION_VIOLATION_ERROR_CODE,
                               'Sum of places is bigger than maximum of available {} out-places'.format(i))
        out_places.append(None if out_max_places is None else out_max_places - cur_sum)
    return out_places


def _get_avail_in_places(layout):
    out_of_order = layout.out_of_order
    layout_data = layout.data
    height = layout_data.shape[0]
    width = layout.width
    out_of_order_places = [0] * height
    for i, data_list in enumerate(out_of_order):
        for _, amount, _ in data_list:
            out_of_order_places[i] += amount
    in_places = []
    for i in range(height):
        cur_sum = 0
        cur_idx = i % width
        for j in range(i, min(i + layout.max_days + 1, height)):
            delta = (layout_data[layout_config.OUT_DATES_COL][j] - layout_data[layout_config.IN_DATES_COL][i]).days
            if np.isnan(delta) or delta < layout.min_days:
                continue
            if delta > layout.max_days:
                break
            if layout_data[get_required_col(cur_idx)][j]:
                cur_sum += layout_data[get_layout_col(cur_idx)][j]
        cur_sum += out_of_order_places[i]
        in_max_places = layout_data[layout_config.IN_PLACES_COL][i]
        if in_max_places is not None and cur_sum > in_max_places:
            raise ErrorMessage(RESTRICTION_VIOLATION_ERROR_CODE,
                               'Sum of places is bigger than maximum of available {} in-places'.format(i))
        in_places.append(None if in_max_places is None else in_max_places - cur_sum)
    return in_places


def _get_corrected_relations(layout):
    data = layout.data
    height = data.shape[0]
    vars_num = 0
    corrected_relations = []
    for i in range(height):
        cur_req_idx = get_required_col(i % layout.width)
        relations = layout.relations if layout.date_relations[i] is None else layout.date_relations[i]
        relations_sum = 0
        for j in range(i, min(i + layout.max_days + 1, height)):
            delta = (data[layout_config.OUT_DATES_COL][j] - data[layout_config.IN_DATES_COL][i]).days
            if np.isnan(delta) or delta < layout.min_days:
                continue
            if delta > layout.max_days:
                break
            if not data[cur_req_idx][j]:
                vars_num += 1
                relations_sum += relations[delta - layout.min_days]
        if relations_sum > 0:
            coef = 1. / relations_sum
        else:
            coef = 0
        corr_relations = [rel * coef for rel in relations]
        corrected_relations.append(corr_relations)
    return corrected_relations, vars_num


def _check_ooo_durations(layout):
    for i in range(layout.data.shape[0]):
        for j, _, _ in layout.out_of_order[i]:
            error_message = 'Out of order cell cannot be placed in {}-{} cell.'.format(i + 1, j + 1)
            if j >= layout.data[layout_config.OUT_DATES_COL].shape[0]:
                raise ErrorMessage(OOO_ILLEGAL_PLACE_ERROR_CODE, error_message)
            delta = (layout.data[layout_config.OUT_DATES_COL][j] - layout.data[layout_config.IN_DATES_COL][i]).days
            if np.isnan(delta) or delta > layout.duration_limit or layout.min_days <= delta <= layout.max_days:
                raise ErrorMessage(OOO_ILLEGAL_PLACE_ERROR_CODE, error_message)
