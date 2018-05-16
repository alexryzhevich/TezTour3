from django.db import models


class Layout(models.Model):
    name = models.CharField(max_length=200)
    min_days = models.IntegerField()
    max_days = models.IntegerField()
    duration_limit = models.IntegerField()
    width = models.IntegerField()
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
    filename = models.CharField(max_length=255, null=True)
    edit_token = models.CharField(max_length=36, null=True)
    last_token_update = models.DateTimeField(null=True)
    update_from_file_date = models.DateField(null=True)


class Priority(models.Model):
    layout = models.ForeignKey(Layout, on_delete=models.CASCADE)
    value = models.FloatField()
    order = models.IntegerField()


class MaxPlacesNumber(models.Model):
    IN = 0
    OUT = 1

    KIND_OF_DIRECTIONS = (
        (IN, 'in'),
        (OUT, 'out'),
    )

    layout = models.ForeignKey(Layout, on_delete=models.CASCADE)
    date = models.DateField(null=True)
    amount = models.IntegerField(null=True)
    direction = models.IntegerField(choices=KIND_OF_DIRECTIONS, default=IN)
    no_losses = models.BooleanField(default=False)


class DatePriority(models.Model):
    layout = models.ForeignKey(Layout, on_delete=models.CASCADE)
    in_date = models.ForeignKey(MaxPlacesNumber, on_delete=models.CASCADE)
    value = models.FloatField()
    order = models.IntegerField()


class PlacesNumber(models.Model):
    layout = models.ForeignKey(Layout, on_delete=models.CASCADE)
    in_max_places = models.ForeignKey(MaxPlacesNumber, related_name='in_max_places', on_delete=models.CASCADE)
    out_max_places = models.ForeignKey(MaxPlacesNumber, related_name='out_max_places', on_delete=models.CASCADE)
    amount = models.IntegerField()
    required = models.BooleanField(default=False)


class OutOfOrderPlacesNumber(models.Model):
    layout = models.ForeignKey(Layout, on_delete=models.CASCADE)
    in_date = models.ForeignKey(MaxPlacesNumber, related_name='in_date', on_delete=models.CASCADE)
    out_date = models.ForeignKey(MaxPlacesNumber, related_name='out_date', on_delete=models.CASCADE)
    amount = models.IntegerField()
    auto_changed = models.BooleanField(default=False)
