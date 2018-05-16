import pandas as pd
import numpy as np

from core.config.layout import IN_DATES_COL, IN_PLACES_COL, OUT_DATES_COL, OUT_PLACES_COL
from core.layout.util import get_layout_col, get_required_col, DATE_FORMAT
import core.layout.layout as core_layout

from layouts.models import Layout, MaxPlacesNumber, Priority, PlacesNumber, DatePriority, OutOfOrderPlacesNumber


def get_layout_from_db(layout: Layout):
    relations = get_layout_relations_from_db(layout)

    in_places_idxs = {}
    out_places_idxs = {}

    in_dates, in_places, out_dates, out_places, no_losses = _get_max_places(layout, in_places_idxs, out_places_idxs)
    date_relations = _get_date_priorities(layout, in_places_idxs, len(in_dates), len(relations))
    data = _init_data_frame(layout, in_dates, in_places, out_dates, out_places)
    _fill_places_data(layout, in_places_idxs, out_places_idxs, data)
    out_of_order = _get_out_of_order(layout, in_places_idxs, out_places_idxs, len(in_dates))

    layout_obj = core_layout.Layout(layout.name, data, date_relations, out_of_order, _get_last_update_date(layout),
                                    no_losses, layout.width, layout.min_days, layout.max_days, layout.duration_limit,
                                    relations, layout.id)
    return layout_obj


def get_layout_relations_from_db(layout: Layout):
    return [pr.value for pr in Priority.objects.filter(layout=layout).order_by('order')]


def _get_last_update_date(layout: Layout):
    if layout.update_from_file_date is None:
        return None
    return layout.update_from_file_date.strftime(DATE_FORMAT)


def _get_max_places(layout: Layout, in_places_idxs: dict, out_places_idxs: dict):
    in_dates = []
    in_places = []
    out_dates = []
    out_places = []
    in_out_max_places = MaxPlacesNumber.objects.filter(layout=layout).order_by('id')
    no_losses = [[False, False] for _ in range(in_out_max_places.count() // 2)]
    for max_places in in_out_max_places:
        if max_places.direction == MaxPlacesNumber.IN:
            in_places_idxs[max_places.id] = len(in_dates)
            no_losses[len(in_dates)][0] = max_places.no_losses
            in_dates.append(None if max_places.date is None else pd.Timestamp(max_places.date))
            in_places.append(max_places.amount)
        else:
            out_places_idxs[max_places.id] = len(out_dates)
            no_losses[len(out_dates)][1] = max_places.no_losses
            out_dates.append(None if max_places.date is None else pd.Timestamp(max_places.date))
            out_places.append(max_places.amount)
    return in_dates, in_places, out_dates, out_places, no_losses


def _get_date_priorities(layout: Layout, in_places_idxs: dict, in_dates_number: int, durations_number: int):
    date_priorities = DatePriority.objects.filter(layout=layout).order_by('id').select_related('in_date')
    date_relations = [None] * in_dates_number
    for priority in date_priorities:
        idx = in_places_idxs[priority.in_date_id]
        if date_relations[idx] is None:
            date_relations[idx] = [0] * durations_number
        date_relations[idx][priority.order] = priority.value
    return date_relations


def _init_data_frame(layout: Layout, in_dates: list, in_places: list, out_dates: list, out_places: list):
    data = pd.DataFrame()
    data[IN_DATES_COL] = np.array(in_dates)
    data[IN_PLACES_COL] = np.array(in_places)
    for i in range(layout.width):
        data = data.assign(**{get_layout_col(i): data[IN_PLACES_COL].apply(lambda _: None)})
    data[OUT_DATES_COL] = np.array(out_dates)
    data[OUT_PLACES_COL] = np.array(out_places)
    for i in range(layout.width):
        data = data.assign(**{get_required_col(i): data[IN_PLACES_COL].apply(lambda _: False)})
    return data


def _fill_places_data(layout: Layout, in_places_idxs: dict, out_places_idxs: dict, data: pd.DataFrame):
    places = PlacesNumber.objects.filter(layout=layout).order_by('in_max_places_id', 'out_max_places_id') \
        .select_related('in_max_places', 'out_max_places')
    col_idxs = {}
    values = {}
    required = {}
    for pl in places:
        i = in_places_idxs[pl.in_max_places_id] % layout.width
        j = out_places_idxs[pl.out_max_places_id]
        if i not in col_idxs:
            col_idxs[i] = []
            values[i] = []
            required[i] = []
        col_idxs[i].append(j)
        values[i].append(pl.amount)
        required[i].append(pl.required)
        # data[get_layout_col(i)][j] = pl.amount
    for i in col_idxs:
        col_vals = np.array(values[i])
        col_reqs = np.array(required[i])
        data[get_layout_col(i)][col_idxs[i]] = col_vals
        data[get_required_col(i)][col_idxs[i]] = col_reqs


def _get_out_of_order(layout: Layout, in_places_idxs: dict, out_places_idxs: dict, dates_number: int):
    out_of_order = [[] for _ in range(dates_number)]
    out_of_order_data = OutOfOrderPlacesNumber.objects.filter(layout=layout).select_related('in_date', 'out_date')
    for data in out_of_order_data:
        out_of_order[in_places_idxs[data.in_date_id]].append((out_places_idxs[data.out_date_id], data.amount,
                                                              data.auto_changed))
    return out_of_order
