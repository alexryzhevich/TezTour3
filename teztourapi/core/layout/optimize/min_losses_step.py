import numpy as np
from scipy.optimize import linprog

from core.layout.layout import Layout
from core.config import layout as layout_config, parameters as param_config
from core.layout.util import get_layout_col, get_required_col
from exceptions.exceptions import COULD_NOT_OPTIMIZE_ERROR


def min_losses_step(layout: Layout, avail_in_places, avail_out_places, vars_num: int):
    inequalities = _get_restrictions(layout, vars_num, avail_in_places, avail_out_places)
    goal = _get_goal(vars_num)
    bounds = [(0., 250.) for _ in range(vars_num)]
    solution = _apply_simplex(np.array([], dtype=float), inequalities, goal, bounds)
    _fill_layout_with_result(layout, solution)


def _apply_simplex(equalities, inequalities, goal, bounds):
    A_ub = inequalities.T[:-1].T if inequalities.shape[0] > 0 else None
    b_ub = inequalities.T[-1] if inequalities.shape[0] > 0 else None
    A_eq = equalities.T[:-1].T if equalities.shape[0] > 0 else None
    b_eq = equalities.T[-1] if equalities.shape[0] > 0 else None
    c = goal
    res = linprog(c, A_ub, b_ub, A_eq, b_eq, bounds=bounds, method='simplex', options={'maxiter': 10000})
    # print('==============================================')
    # print(res['fun'])
    if res['success']:
        optimal = res['x'].astype(int)
        return optimal
    raise COULD_NOT_OPTIMIZE_ERROR


def _fill_layout_with_result(layout, result):
    data = layout.data
    height = data[layout_config.IN_PLACES_COL].shape[0]
    cur_var_idx = 0
    col_idxs = {}
    values = {}
    for i in range(height):
        column_idx = i % layout.width
        if data[layout_config.IN_PLACES_COL][i] is None:
            continue
        cur_idx = get_layout_col(column_idx)
        cur_req_idx = get_required_col(column_idx)
        # res_places = 0
        max_places = data[layout_config.IN_PLACES_COL][i]
        for j in range(i, min(i + param_config.MAX_DAYS + 1, height)):
            delta = (data[layout_config.OUT_DATES_COL][j] - data[layout_config.IN_DATES_COL][i]).days
            if np.isnan(delta) or delta < layout.min_days:
                continue
            if delta > layout.max_days:
                break
            if data[cur_req_idx][j]:
                continue
            if column_idx not in col_idxs:
                col_idxs[column_idx] = []
                values[column_idx] = []
            col_idxs[column_idx].append(j)
            values[column_idx].append(result[cur_var_idx])

            #data[cur_idx][j] = result[cur_var_idx]
            # res_places += result[cur_var_idx]
            cur_var_idx += 1
        # data[cur_idx][i] = res_places if res_places > max_places else max_places
    for column_idx in col_idxs:
        col_vals = np.array(values[column_idx])
        data[get_layout_col(column_idx)][col_idxs[column_idx]] = col_vals


def _get_goal(vars_num):
    return np.full(vars_num, -1.)


def _get_restrictions(layout, vars_num, avail_in_places, avail_out_places):
    height = layout.data.shape[0]
    data = layout.data
    boundary_inequalities = []
    out_inequalities = {}
    cur_var_idx = 0
    for i, avail_in_places in zip(range(height), avail_in_places):
        column_idx = i % layout.width
        if avail_in_places is None:
            continue
        cur_req_idx = get_required_col(column_idx)
        cur_col_idx = get_layout_col(column_idx)
        to_add_idx = []
        for j in range(i, min(i + param_config.MAX_DAYS + 1, height)):
            delta = (data[layout_config.OUT_DATES_COL][j] - data[layout_config.IN_DATES_COL][i]).days
            if np.isnan(delta) or delta < layout.min_days:
                continue
            if delta > layout.max_days:
                break
            if data[cur_req_idx][j]:
                continue
            to_add_idx.append(cur_var_idx)
            _add_horizontal_restriction(out_inequalities, j, vars_num, cur_var_idx, avail_out_places[j])
            _add_lb_restriction(boundary_inequalities, cur_var_idx, vars_num, data[cur_col_idx][j])
            cur_var_idx += 1
        if len(to_add_idx) > 0:
            _add_ub_vertical_restriction(boundary_inequalities, to_add_idx, vars_num, avail_in_places)
    for key in out_inequalities:
        boundary_inequalities.append(out_inequalities[key])
    boundary_inequalities = np.array(boundary_inequalities)
    return boundary_inequalities


def _add_lb_restriction(inequalities, idx, vars_num, value):
    ineq = np.zeros(vars_num + 1)
    ineq[idx] = -1.
    ineq[-1] = -value
    inequalities.append(ineq)


def _add_ub_vertical_restriction(inequalities, to_add_idx, vars_num, avail_places):
    ineq = np.zeros(vars_num + 1)
    ineq[to_add_idx] = 1
    ineq[-1] = avail_places
    inequalities.append(ineq)


def _add_horizontal_restriction(out_inequalities, line_idx, vars_num, cur_var_idx, avail_out_places):
    if line_idx not in out_inequalities:
        out_inequalities[line_idx] = np.zeros(vars_num + 1)
        out_inequalities[line_idx][-1] = avail_out_places
    out_inequalities[line_idx][cur_var_idx] = 1
