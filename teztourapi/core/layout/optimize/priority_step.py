import numpy as np
import pandas as pd

from core.layout.layout import Layout
from core.config import layout as layout_config
from core.layout.util import get_layout_col, get_required_col


def priority_step(layout: Layout, avail_in_places, avail_out_places, corrected_relations, vars_num):
    _set_initial_values(layout, avail_in_places, corrected_relations, vars_num)
    _satisfy_ub_reqs(layout, avail_out_places)


def _set_initial_values(layout: Layout, avail_in_places, corr_relations, vars_num):
    height = layout.data[layout_config.IN_PLACES_COL].shape[0]
    init_values = [[] for _ in range(layout.width)]
    init_idxs = [[] for _ in range(layout.width)]
    for i in range(height):
        cur_idx = i % layout.width
        cur_init_values = [int(pr * avail_in_places[i]) if avail_in_places[i] is not None else None for pr in corr_relations[i]]
        for j in range(i, min(i + layout.max_days + 1, height)):
            delta = (layout.data[layout_config.OUT_DATES_COL][j] - layout.data[layout_config.IN_DATES_COL][i]).days
            if np.isnan(delta) or delta < layout.min_days:
                continue
            if delta > layout.max_days:
                break
            cur_init_idx = delta - layout.min_days
            if not layout.data[get_required_col(cur_idx)][j]:
                init_idxs[cur_idx].append(j)
                init_values[cur_idx].append(cur_init_values[cur_init_idx])
    for i in range(layout.width):
        layout.data[get_layout_col(i)][init_idxs[i]] = np.array(init_values[i])
    return vars_num


def _satisfy_ub_reqs(layout: Layout, avail_out_places):
    height = layout.data.shape[0]
    required_idxs = [[] for _ in range(layout.width)]
    required_values = [[] for _ in range(layout.width)]
    for i in range(height):
        if pd.isnull(avail_out_places[i]):
            continue
        col_idxs = []
        col_values = []
        used_sum = 0
        for j in range(layout.width):
            amount = layout.data[get_layout_col(j)][i]
            required = layout.data[get_required_col(j)][i]
            if not required and not pd.isnull(amount):
                col_idxs.append(j)
                col_values.append(int(amount))
                used_sum += int(amount)
        if used_sum <= avail_out_places[i]:
            continue
        coef = avail_out_places[i] / used_sum
        for idx, old_value in zip(col_idxs, col_values):
            required_values[idx].append(int(old_value * coef))
            required_idxs[idx].append(i)
    for i in range(layout.width):
        layout.data[get_layout_col(i)][required_idxs[i]] = np.array(required_values[i])
