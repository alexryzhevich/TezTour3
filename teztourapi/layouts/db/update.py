import datetime

from django.db import transaction

from core.layout.util import DATE_FORMAT
from exceptions.exceptions import DATA_INTEGRITY_ERROR_CODE
from exceptions.structs import ErrorMessage
from layouts.structs import LayoutData

from layouts.models import Layout, MaxPlacesNumber, Priority, PlacesNumber, DatePriority, OutOfOrderPlacesNumber

EPS = 1.e-5


@transaction.atomic
def update_layout_in_db(layout_data: LayoutData, layout: Layout, new_filename: str=None, update_last_update=False):
    _update_layout_filename(layout, new_filename)
    _update_last_update_date(layout, update_last_update)
    _update_layout_priorities(layout_data, layout)

    in_dates_idxs = {}
    in_dates_ids = []
    out_dates_idxs = {}
    out_dates_ids = []

    _update_max_places(layout_data, layout, in_dates_idxs, in_dates_ids, out_dates_idxs, out_dates_ids)
    _merge_date_priorities(layout_data, layout, in_dates_idxs, in_dates_ids)
    _update_places(layout_data, layout)
    _merge_out_of_order(layout_data, layout, in_dates_idxs, in_dates_ids, out_dates_idxs, out_dates_ids)


def _update_layout_filename(layout: Layout, new_filename: str=None):
    if new_filename is not None:
        layout.filename = new_filename
        layout.save()


def _update_last_update_date(layout: Layout, update_last_update: bool):
    if not update_last_update:
        return
    layout.update_from_file_date = datetime.datetime.now()
    layout.save()


def _update_layout_priorities(layout_data: LayoutData, layout: Layout):
    priorities = Priority.objects.filter(layout=layout).order_by('order')
    for value, priority in zip(layout_data.priorities, priorities):
        if abs(value - priority.value) > EPS:
            priority.value = value
            priority.save()


def _update_max_places(layout_data: LayoutData, layout: Layout, in_dates_idxs: dict, in_dates_ids: list,
                       out_dates_idxs: dict, out_dates_ids: list):
    in_out_max_places = MaxPlacesNumber.objects.filter(layout=layout).order_by('id')
    in_places_counter = 0
    out_places_counter = 0

    for max_places in in_out_max_places:
        if max_places.direction == MaxPlacesNumber.IN:
            in_amount = layout_data.dates[in_places_counter].in_amount
            no_losses = layout_data.dates[in_places_counter].in_no_losses
            if max_places.amount != in_amount or max_places.no_losses != no_losses:
                max_places.amount = in_amount
                max_places.no_losses = no_losses
                max_places.save()
            in_dates_idxs[max_places.id] = in_places_counter
            in_dates_ids.append(max_places.id)
            in_places_counter += 1
        else:
            out_amount = layout_data.dates[out_places_counter].out_amount
            no_losses = layout_data.dates[out_places_counter].out_no_losses
            if max_places.amount != out_amount or max_places.no_losses != no_losses:
                max_places.amount = out_amount
                max_places.no_losses = no_losses
                max_places.save()
            out_dates_idxs[max_places.id] = out_places_counter
            out_dates_ids.append(max_places.id)
            out_places_counter += 1


def _merge_date_priorities(layout_data: LayoutData, layout: Layout, in_dates_idxs: dict, in_dates_ids: list):
    date_priorities = DatePriority.objects.filter(layout=layout).order_by('id').select_related('in_date')
    delete_list = []
    processed_priorities = [None if d.priorities is None else False for d in layout_data.dates]

    # update existing priorities
    for date_priority in date_priorities:
        idx = in_dates_idxs[date_priority.in_date_id]
        if layout_data.dates[idx].priorities is None:
            delete_list.append(date_priority.id)
            continue
        processed_priorities[idx] = True
        value = layout_data.dates[idx].priorities[date_priority.order]
        if abs(value - date_priority.value) > EPS:
            date_priority.value = value
            date_priority.save()

    # delete extra priorities
    DatePriority.objects.filter(id__in=delete_list).delete()

    # create new priorities
    new_priorities = []
    for i in range(len(layout_data.dates)):
        if processed_priorities[i] is None or processed_priorities[i]:
            continue
        for order, priority in enumerate(layout_data.dates[i].priorities):
            new_priorities.append(DatePriority(layout=layout, in_date_id=in_dates_ids[i], order=order, value=priority))
    if len(new_priorities) > 0:
        DatePriority.objects.bulk_create(new_priorities)


def _update_places(layout_data: LayoutData, layout: Layout):
    # transform new places values to dict to increase searching time
    new_places = {}
    for places in layout_data.places:
        in_date = layout_data.dates[places.in_date].in_date
        out_date = layout_data.dates[places.out_date].out_date
        new_places[in_date + '-' + out_date] = (places.amount, places.required)

    places = PlacesNumber.objects.filter(layout=layout).order_by('in_max_places_id',
                                                                 'out_max_places_id').select_related('in_max_places',
                                                                                                     'out_max_places')
    # update places values in db
    for pl in places:
        in_date = pl.in_max_places.date.strftime(DATE_FORMAT)
        out_date = pl.out_max_places.date.strftime(DATE_FORMAT)
        key = in_date + '-' + out_date
        try:
            (amount, required) = new_places[key]
        except KeyError:
            raise ErrorMessage(DATA_INTEGRITY_ERROR_CODE,
                               'Amount value was not provided for {}-{} places'.format(in_date, out_date))
        if pl.required != required or pl.amount != amount:
            pl.required = required
            pl.amount = amount
            pl.save()


def _merge_out_of_order(layout_data: LayoutData, layout: Layout, in_dates_idxs: dict, in_dates_ids: list,
                        out_dates_idxs: dict, out_dates_ids: list):
    processed_ooo = [False for _ in layout_data.out_of_order]
    ooo_idxs = {'{}-{}'.format(data.in_date, data.out_date): (i, data) for i, data in
                enumerate(layout_data.out_of_order)}
    out_of_order = OutOfOrderPlacesNumber.objects.filter(layout=layout).select_related('in_date', 'out_date')

    # update existing ooo
    delete_list = []
    for pl in out_of_order:
        key = '{}-{}'.format(in_dates_idxs[pl.in_date_id], out_dates_idxs[pl.out_date_id])
        if key in ooo_idxs:
            i, data = ooo_idxs[key]
            processed_ooo[i] = True
            if pl.amount != data.amount or pl.auto_changed != data.auto_changed:
                pl.amount = data.amount
                pl.auto_changed = data.auto_changed
                pl.save()
        else:
            delete_list.append(pl.id)

    # delete extra ooo
    OutOfOrderPlacesNumber.objects.filter(id__in=delete_list).delete()

    # create new ooo
    new_ooo = [
        OutOfOrderPlacesNumber(layout=layout, in_date_id=in_dates_ids[data.in_date], auto_changed=data.auto_changed,
                               out_date_id=out_dates_ids[data.out_date], amount=data.amount)
        for i, data in enumerate(layout_data.out_of_order) if not processed_ooo[i]]
    OutOfOrderPlacesNumber.objects.bulk_create(new_ooo)
