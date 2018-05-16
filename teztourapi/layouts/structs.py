import numpy as np
import pandas as pd
from typing import List

import core.layout.layout as core_layout
from core.config.layout import IN_DATES_COL, OUT_DATES_COL, IN_PLACES_COL, OUT_PLACES_COL
from core.layout.util import ts_to_str, fl_to_int, get_required_col, get_layout_col, str_to_ts

FloatList = List[float]


class OutOfOrderPlacesData(object):
    def __init__(self, in_date: int, out_date: int, amount: int, auto_changed: bool):
        self.in_date = in_date
        self.out_date = out_date
        self.amount = amount
        self.auto_changed = auto_changed


class PlacesData(object):
    def __init__(self, in_date: int, out_date: int, amount: int, required: bool):
        self.in_date = in_date
        self.out_date = out_date
        self.amount = amount
        self.required = required


class DatesData(object):
    def __init__(self, in_date: str, in_amount: int, in_losses: int, out_date: str, out_amount: int, out_losses: int,
                 in_no_losses: bool, out_no_losses: bool, priorities: FloatList = None):
        self.in_date = in_date
        self.in_amount = in_amount
        self.in_losses = in_losses
        self.out_date = out_date
        self.out_amount = out_amount
        self.out_losses = out_losses
        self.in_no_losses = in_no_losses
        self.out_no_losses = out_no_losses
        self.priorities = priorities


PlacesList = List[PlacesData]
DatesList = List[DatesData]
OutOfOrderList = List[OutOfOrderPlacesData]


class LayoutData(object):
    def __init__(self, id: int, name: str, places: PlacesList, dates: DatesList, width: int, min_days: int,
                 max_days: int, priorities: FloatList, out_of_order: OutOfOrderList, duration_limit: int,
                 update_from_file_date: str):
        self.id = id
        self.name = name
        self.places = places
        self.dates = dates
        self.width = width
        self.min_days = min_days
        self.max_days = max_days
        self.duration_limit = duration_limit
        self.priorities = priorities
        self.out_of_order = out_of_order
        self.update_from_file_date = update_from_file_date

    @staticmethod
    def from_layout(layout_obj: core_layout.Layout):
        data = layout_obj.data
        height = data.shape[0]

        dates = [DatesData(ts_to_str(data[IN_DATES_COL][i]), fl_to_int(data[IN_PLACES_COL][i]),
                           fl_to_int(data[IN_PLACES_COL][i]), ts_to_str(data[OUT_DATES_COL][i]),
                           fl_to_int(data[OUT_PLACES_COL][i]), fl_to_int(data[OUT_PLACES_COL][i]),
                           layout_obj.no_losses[i][0], layout_obj.no_losses[i][1],
                           layout_obj.date_relations[i]) for i in range(height)]

        places = []
        current_idx = 0
        for i in range(height):
            for j in range(i, min(i + layout_obj.max_days + 1, height)):
                delta = (data[OUT_DATES_COL][j] - data[IN_DATES_COL][i]).days
                if np.isnan(delta) or delta < layout_obj.min_days:
                    continue
                if delta > layout_obj.max_days:
                    break
                places.append(PlacesData(i, j, fl_to_int(data[get_layout_col(current_idx)][j]),
                                         bool(data[get_required_col(current_idx)][j])))
            current_idx = (current_idx + 1) % layout_obj.width
        out_of_order = []
        for i, out_of_order_list in enumerate(layout_obj.out_of_order):
            out_of_order += [OutOfOrderPlacesData(i, *data) for data in out_of_order_list]
        for place in places:
            dates[place.in_date].in_losses -= place.amount
            dates[place.out_date].out_losses -= place.amount
        for ooo in out_of_order:
            dates[ooo.in_date].in_losses -= ooo.amount
            dates[ooo.out_date].out_losses -= ooo.amount
        return LayoutData(layout_obj.id, layout_obj.name, places, dates, layout_obj.width, layout_obj.min_days,
                          layout_obj.max_days, layout_obj.relations, out_of_order, layout_obj.duration_limit,
                          layout_obj.update_date)

    def to_layout(self):
        in_dates = []
        in_places = []
        out_dates = []
        out_places = []
        date_priorities = []
        no_losses = []
        for date in self.dates:
            in_dates.append(str_to_ts(date.in_date))
            in_places.append(date.in_amount)
            out_dates.append(str_to_ts(date.out_date))
            out_places.append(date.out_amount)
            no_losses.append([date.in_no_losses, date.out_no_losses])
            date_priorities.append(date.priorities)

        data = pd.DataFrame()
        data[IN_DATES_COL] = np.array(in_dates)
        data[IN_PLACES_COL] = np.array(in_places)
        for i in range(self.width):
            data = data.assign(**{get_layout_col(i): data[IN_PLACES_COL].apply(lambda _: None)})
        data[OUT_DATES_COL] = np.array(out_dates)
        data[OUT_PLACES_COL] = np.array(out_places)
        for i in range(self.width):
            data = data.assign(**{get_required_col(i): data[IN_PLACES_COL].apply(lambda _: False)})

        col_idxs = {}
        values = {}
        required = {}
        for pl in self.places:
            i = pl.in_date % self.width
            j = pl.out_date
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

        out_of_order = [[] for _ in data[IN_DATES_COL]]
        for ooo_data in self.out_of_order:
            out_of_order[ooo_data.in_date].append((ooo_data.out_date, ooo_data.amount, ooo_data.auto_changed))

        layout_obj = core_layout.Layout(self.name, data, date_priorities, out_of_order, self.update_from_file_date,
                                        no_losses, self.width, self.min_days, self.max_days, self.duration_limit,
                                        self.priorities, self.id)
        return layout_obj


