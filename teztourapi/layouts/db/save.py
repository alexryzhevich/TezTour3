import datetime
import pandas as pd
import numpy as np

from django.db import transaction

from core.config.layout import IN_DATES_COL, IN_PLACES_COL, OUT_DATES_COL, OUT_PLACES_COL
from core.layout.util import DATE_FORMAT, get_layout_col
import core.layout.layout as core_layout

from layouts.models import MaxPlacesNumber, Layout, DatePriority, PlacesNumber, OutOfOrderPlacesNumber, Priority


@transaction.atomic
def save_new_layout_to_db(layout_obj: core_layout.Layout, layout: Layout):
    _save_start_end_dates(layout_obj, layout)

    in_dates_ids = _save_max_places_number(layout_obj, layout, dir_in=True)
    out_dates_ids = _save_max_places_number(layout_obj, layout, dir_in=False)

    _save_date_priorities(layout_obj, layout, in_dates_ids)
    _save_places_number(layout_obj, layout, in_dates_ids, out_dates_ids)
    _save_out_of_order(layout_obj, layout, in_dates_ids, out_dates_ids)


def save_layout_priorities(layout: Layout, relations):
    for rel, i in zip(relations, range(len(relations))):
        priority = Priority(order=i, value=rel, layout=layout)
        priority.save()


def _save_start_end_dates(layout_obj: core_layout.Layout, layout: Layout):
    first_non_null_date = layout_obj.data[-layout_obj.data[IN_DATES_COL].isnull()][IN_DATES_COL][0]
    last_non_null_date = layout_obj.data[-layout_obj.data[IN_DATES_COL].isnull()][IN_DATES_COL].iloc[-1]

    layout.start_date = datetime.datetime.strptime(first_non_null_date.strftime(DATE_FORMAT), DATE_FORMAT)
    layout.end_date = datetime.datetime.strptime(last_non_null_date.strftime(DATE_FORMAT), DATE_FORMAT)
    layout.update_from_file_date = datetime.datetime.now()
    layout.save()


def _save_max_places_number(layout_obj: core_layout.Layout, layout: Layout, dir_in: bool=True):
    dates_col = IN_DATES_COL if dir_in else OUT_DATES_COL
    places_col = IN_PLACES_COL if dir_in else OUT_PLACES_COL
    direction = MaxPlacesNumber.IN if dir_in else MaxPlacesNumber.OUT
    no_losses_idx = 0 if dir_in else 1
    dates_ids = []
    for i in range(layout_obj.data.shape[0]):
        ts = layout_obj.data[dates_col][i]
        places = None if pd.isnull(layout_obj.data[places_col][i]) else int(layout_obj.data[places_col][i])
        date = datetime.datetime.strptime(ts.strftime(DATE_FORMAT), DATE_FORMAT) if not pd.isnull(ts) else None
        no_losses = layout_obj.no_losses[i][no_losses_idx]
        max_places = MaxPlacesNumber(direction=direction, date=date, amount=places, layout=layout, no_losses=no_losses)
        max_places.save()
        dates_ids.append(max_places.id)
    return dates_ids


def _save_date_priorities(layout_obj: core_layout.Layout, layout: Layout, in_dates_ids: list):
    date_priorities = []
    for i, priorities in enumerate(layout_obj.date_relations):
        if priorities is None:
            continue
        for order, priority in enumerate(priorities):
            date_priorities.append(DatePriority(layout=layout, in_date_id=in_dates_ids[i], order=order, value=priority))
    if len(date_priorities) > 0:
        DatePriority.objects.bulk_create(date_priorities)


def _save_places_number(layout_obj: core_layout.Layout, layout: Layout, in_dates_ids: list, out_dates_ids: list):
    places_to_create = []
    current_idx = 0
    for i in range(layout_obj.data.shape[0]):
        for j in range(i, min(i + layout_obj.max_days + 1, layout_obj.data.shape[0])):
            delta = (layout_obj.data[OUT_DATES_COL][j] - layout_obj.data[IN_DATES_COL][i]).days
            if np.isnan(delta) or delta < layout_obj.min_days:
                continue
            if delta > layout_obj.max_days:
                break
            amount = layout_obj.data[get_layout_col(current_idx)][j]
            amount = None if pd.isnull(amount) else int(amount)
            if amount is None:
                continue
            places = PlacesNumber(amount=amount, layout=layout,
                                  in_max_places_id=in_dates_ids[i], out_max_places_id=out_dates_ids[j])
            places_to_create.append(places)
        current_idx = (current_idx + 1) % layout.width
    PlacesNumber.objects.bulk_create(places_to_create)


def _save_out_of_order(layout_obj: core_layout.Layout, layout: Layout, in_dates_ids: list, out_dates_ids: list):
    out_of_order = []
    for i, data in enumerate(layout_obj.out_of_order):
        out_of_order += [OutOfOrderPlacesNumber(layout=layout, in_date_id=in_dates_ids[i], auto_changed=ac,
                                                out_date_id=out_dates_ids[j], amount=am) for j, am, ac in data]
    OutOfOrderPlacesNumber.objects.bulk_create(out_of_order)
