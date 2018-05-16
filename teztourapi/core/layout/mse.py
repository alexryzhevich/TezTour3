import numpy as np
import pandas as pd
from scipy.optimize import minimize

from core.layout.layout import Layout
from core.config import layout as layout_config, parameters as param_config
from core.layout.util import get_layout_col, get_required_col, DATE_FORMAT
from exceptions.exceptions import RESTRICTION_VIOLATION_ERROR_CODE, COULD_NOT_OPTIMIZE_ERROR, \
    OOO_ILLEGAL_PLACE_ERROR_CODE
from exceptions.structs import ErrorMessage


def mse(layout: Layout, last_update: str=None):
    _null_prev_day_values(layout, last_update)
    _check_ooo_durations(layout)
    corrected_relations, vars_num = _get_corrected_relations(layout)
    avail_in_places = _get_avail_in_places(layout)
    avail_out_places = _get_avail_out_places(layout)
    col_ineqs, row_ineqs, pr_goals = _get_restrictions(layout, avail_in_places, avail_out_places, corrected_relations)
    bounds = [(0., 250.) for _ in range(vars_num)]

    solution = _apply_minimize(col_ineqs, row_ineqs, pr_goals, bounds,  vars_num)
    _fill_layout_with_result(layout, solution)
    return layout


def _apply_minimize(col_ineqs, row_ineqs, pr_goals, bounds, vars_num):
    constraints = []
    _form_ineqs(constraints, col_ineqs)
    _form_ineqs(constraints, row_ineqs)
    goal = lambda x, prs: np.sum((x - prs) ** 2.0)
    jac = lambda x, prs: (x - prs) * 2.0
    x0 = np.zeros(vars_num)
    res = minimize(fun=goal, x0=x0, jac=jac, args=pr_goals, method='COBYLA', bounds=bounds, constraints=constraints,
                   options={'maxiter': 10000})
    print('==============================================')
    print(res['fun'])
    if res['success']:
        optimal = res['x'].astype(int)
        return optimal
    raise COULD_NOT_OPTIMIZE_ERROR


def _form_ineqs(res_ineqs, source_ineqs):
    for idxs, val in source_ineqs:
        res_ineqs.append({
            'type': 'ineq',
            'fun': lambda x, x_idxs, max_val: max_val - np.sum(x[x_idxs]),
            'jac': lambda x, x_idxs, max_val: calc_jac(x, x_idxs),
            'args': (idxs, val)
        })


def calc_jac(x, x_idxs):
    jac = np.empty_like(x)
    jac[x_idxs] = -1.
    return jac


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
        res_places = 0
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
            res_places += result[cur_var_idx]
            cur_var_idx += 1
        data[cur_idx][i] = res_places if res_places > max_places else max_places
    for column_idx in col_idxs:
        col_vals = np.array(values[column_idx])
        data[get_layout_col(column_idx)][col_idxs[column_idx]] = col_vals


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
    height = layout.data.shape[0]
    data = layout.data
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


def _get_restrictions(layout, avail_in_places, avail_out_places, corr_relations):
    height = layout.data.shape[0]
    data = layout.data
    col_ineqs = []
    row_ineqs = []
    pr_goals = []
    out_inequalities = {}
    cur_var_idx = 0
    for i, avail_in_places, corr_relation in zip(range(height), avail_in_places, corr_relations):
        column_idx = i % layout.width
        if avail_in_places is None:
            continue
        cur_req_idx = get_required_col(column_idx)
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
            _add_horizontal_restriction(out_inequalities, j, cur_var_idx, avail_out_places[j])
            _add_priority_goal(pr_goals, corr_relation[delta - layout.min_days], avail_in_places)
            cur_var_idx += 1
        if len(to_add_idx) > 0:
            _add_ub_vertical_restriction(col_ineqs, to_add_idx, avail_in_places)
    for key in out_inequalities:
        row_ineqs.append(out_inequalities[key])
    return col_ineqs, row_ineqs, np.array(pr_goals)


def _add_ub_vertical_restriction(inequalities, to_add_idx, avail_places):
    inequalities.append((list(to_add_idx), avail_places))


def _add_horizontal_restriction(out_inequalities, line_idx, cur_var_idx, avail_out_places):
    if line_idx not in out_inequalities:
        out_inequalities[line_idx] = ([], avail_out_places)
    out_inequalities[line_idx][0].append(cur_var_idx)


def _add_priority_goal(goals, priority, avail_places):
    goals.append(int(priority * avail_places))
