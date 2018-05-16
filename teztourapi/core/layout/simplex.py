import numpy as np
import pandas as pd
from scipy.optimize import linprog

from core.layout.layout import Layout
from core.config import layout as layout_config, parameters as param_config
from core.layout.util import get_layout_col, get_required_col, DATE_FORMAT
from exceptions.exceptions import RESTRICTION_VIOLATION_ERROR_CODE, COULD_NOT_OPTIMIZE_ERROR, \
    OOO_ILLEGAL_PLACE_ERROR_CODE
from exceptions.structs import ErrorMessage


def simplex(layout: Layout, last_update: str=None):
    #_null_prev_day_values(layout, last_update)
    equalities, ub_inequalities, priority_inequalities, goal, bounds = _fill_parameters(layout)
    step1_inequalities = ub_inequalities if priority_inequalities.size == 0 else np.vstack((ub_inequalities, priority_inequalities))
    solution = _apply_simplex(equalities, step1_inequalities, goal, bounds)
    lb_inequalities = _get_lb_restrictions(solution)
    solution = _apply_simplex(equalities, np.vstack((ub_inequalities, lb_inequalities)), goal, bounds)
    _fill_layout_with_result(layout, solution)
    return layout


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


def _fill_parameters(layout: Layout):
    data = layout.data
    height = data[layout_config.IN_PLACES_COL].shape[0]
    column_idx = 0
    vars_num = 0
    corr_relations = []
    max_places = []
    avail_places = []
    for i in range(height):
        cur_max_places, cur_avail_places, cur_corr_relations, cur_vars_num = _get_corrected_relations(layout, i, height, column_idx)
        max_places.append(cur_max_places)
        avail_places.append(cur_avail_places)
        corr_relations.append(cur_corr_relations)
        vars_num += cur_vars_num
        column_idx = (column_idx + 1) % layout.width
    avail_out_places = _get_avail_out_places(data, height, layout.width, layout.out_of_order)
    equalities, boundary_inequalities, priority_inequalities = _get_restrictions(layout, height, max_places, avail_places, corr_relations, vars_num,
                                                 avail_out_places)
    goal = _get_goal(vars_num)
    bounds = [(0., 250.) for _ in range(vars_num)]  # TODO vars bounds
    return equalities, boundary_inequalities, priority_inequalities, goal, bounds


def _get_avail_out_places(layout_data, height, width, out_of_order):
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


def _get_corrected_relations(layout, i, height, column_idx):
    data = layout.data
    max_places = data[layout_config.IN_PLACES_COL][i]
    if max_places is None:
        return max_places, None, [], 0
    _check_ooo_durations(layout, i)
    cur_idx = get_layout_col(column_idx)
    cur_req_idx = get_required_col(column_idx)
    relations = layout.relations if layout.date_relations[i] is None else layout.date_relations[i]
    relations_sum = 0
    used_sum = sum((amount for _, amount, _ in layout.out_of_order[i])) if len(layout.out_of_order[i]) > 0 else 0
    vars_num = 0
    for j in range(i, min(i + param_config.MAX_DAYS + 1, height)):
        delta = (data[layout_config.OUT_DATES_COL][j] - data[layout_config.IN_DATES_COL][i]).days
        if np.isnan(delta) or delta < layout.min_days:
            continue
        if delta > layout.max_days:
            break
        if not data[cur_req_idx][j]:
            vars_num += 1
            relations_sum += relations[delta - layout.min_days]
        else:
            used_sum += data[cur_idx][j]
    if relations_sum > 0:
        coef = 1. / relations_sum
    else:
        coef = 0
    corrected_relations = [rel * coef for rel in relations]
    if used_sum > max_places:
        raise ErrorMessage(RESTRICTION_VIOLATION_ERROR_CODE,
                           'Sum of places is bigger than maximum of available {} in-places'.format(i))
    else:
        avail_places = max_places - used_sum
    return max_places, avail_places, corrected_relations, vars_num


def _check_ooo_durations(layout, i):
    for j, _, _ in layout.out_of_order[i]:
        error_message = 'Out of order cell cannot be placed in {}-{} cell.'.format(i + 1, j + 1)
        if j >= layout.data[layout_config.OUT_DATES_COL].shape[0]:
            raise ErrorMessage(OOO_ILLEGAL_PLACE_ERROR_CODE, error_message)
        delta = (layout.data[layout_config.OUT_DATES_COL][j] - layout.data[layout_config.IN_DATES_COL][i]).days
        if np.isnan(delta) or delta > layout.duration_limit or layout.min_days <= delta <= layout.max_days:
            raise ErrorMessage(OOO_ILLEGAL_PLACE_ERROR_CODE, error_message)


def _get_goal(vars_num):
    return np.full(vars_num, -1.)


def _get_restrictions(layout, height, all_max_places, all_avail_places, all_corr_relations, vars_num, avail_out_places):
    data = layout.data
    equalities = []
    boundary_inequalities = []
    priority_inequalities = []
    out_inequalities = {}
    cur_var_idx = 0
    for i, max_places, avail_places, corr_relations in zip(range(height), all_max_places, all_avail_places, all_corr_relations):
        column_idx = i % layout.width
        if avail_places is None:
            continue
        cur_req_idx = get_required_col(column_idx)
        to_add_idx = []
        to_add_rel = []
        col_idxs = []
        # data[cur_idx][i] = max_places  # remove
        for j in range(i, min(i + param_config.MAX_DAYS + 1, height)):
            delta = (data[layout_config.OUT_DATES_COL][j] - data[layout_config.IN_DATES_COL][i]).days
            if np.isnan(delta) or delta < layout.min_days:
                continue
            if delta > layout.max_days:
                break
            if data[cur_req_idx][j]:
                continue
            to_add_idx.append(cur_var_idx)
            to_add_rel.append(corr_relations[delta - layout.min_days])
                # data[cur_idx][j] = int(avail_places * corr_relations[delta - layout.min_days])   # remove
            # else:
            #     _add_strict_restriction(equalities, data, j, cur_idx, vars_num, cur_var_idx)
            _add_horizontal_restriction(out_inequalities, j, vars_num, cur_var_idx, avail_out_places[j])
            col_idxs.append(cur_var_idx)
            cur_var_idx += 1
        if len(to_add_idx) > 1:
            _add_relational_restrictions(priority_inequalities, to_add_idx, to_add_rel, vars_num)
        if len(to_add_idx) > 0:
            _add_ub_vertical_restriction(boundary_inequalities, to_add_idx, vars_num, avail_places)
            #_add_lb_vertical_restriction(inequalities, col_idxs, vars_num, max_places)
    for key in out_inequalities:
        boundary_inequalities.append(out_inequalities[key])
    #_add_bounds_restrictions(inequalities, vars_num)
    equalities = np.array(equalities)
    boundary_inequalities = np.array(boundary_inequalities)
    priority_inequalities = np.array(priority_inequalities)
    return equalities, boundary_inequalities, priority_inequalities


def _get_lb_restrictions(solution):
    inequalities = np.zeros((solution.size, solution.size + 1))
    inequalities[:, -1] = -solution
    np.fill_diagonal(inequalities, -1.)
    return inequalities


def _add_bounds_restrictions(inequalities, vars_num):
    for i in range(vars_num):
        ineq = np.zeros(vars_num + 1)
        ineq[i] = -1.
        ineq[-1] = -1.
        inequalities.append(ineq)


def _add_ub_vertical_restriction(inequalities, to_add_idx, vars_num, avail_places):
    ineq = np.zeros(vars_num + 1)
    ineq[to_add_idx] = 1
    ineq[-1] = avail_places
    inequalities.append(ineq)


def _add_lb_vertical_restriction(inequalities, col_idxs, vars_num, max_places):
    ineq = np.zeros(vars_num + 1)
    ineq[col_idxs] = -1
    ineq[-1] = -0.1 * max_places
    inequalities.append(ineq)


def _add_horizontal_restriction(out_inequalities, line_idx, vars_num, cur_var_idx, avail_out_places):
    if line_idx not in out_inequalities:
        out_inequalities[line_idx] = np.zeros(vars_num + 1)
        out_inequalities[line_idx][-1] = avail_out_places
    out_inequalities[line_idx][cur_var_idx] = 1


def _add_strict_restriction(equalities, layout_data, line_idx, col_idx, vars_num, cur_var_idx):
    eq = np.zeros(vars_num + 1)
    eq[cur_var_idx] = 1
    eq[-1] = layout_data[col_idx][line_idx]
    equalities.append(eq)


def _add_relational_restrictions(inequalities, var_indexes, var_relations, vars_num):
    for idx, rel in zip(var_indexes, var_relations):
        ineq = np.zeros(vars_num + 1)
        ineq[var_indexes] = rel
        ineq[idx] = rel - 1
        inequalities.append(ineq)

        # lb_rel = max(0., rel - 0.1)
        # ineq = np.zeros(vars_num + 1)
        # ineq[var_indexes] = lb_rel
        # ineq[idx] = lb_rel - 1.
        # inequalities.append(ineq)
        # ub_rel = min(1., rel + 0.1)
        # ineq = np.zeros(vars_num + 1)
        # ineq[var_indexes] = -ub_rel
        # ineq[idx] = 1. - ub_rel
        # inequalities.append(ineq)

        # lb_rel = max(0., rel - 0.1)
        # ineq = np.zeros(vars_num + 1)
        # ineq[idx] = -1.
        # ineq[-1] = -lb_rel * available_places
        # inequalities.append(ineq)
        # ub_rel = min(1., rel + 0.1)
        # ineq = np.zeros(vars_num + 1)
        # ineq[idx] = 1.
        # ineq[-1] = ub_rel * available_places
        # inequalities.append(ineq)
