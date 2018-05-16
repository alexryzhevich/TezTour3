from rest_framework import serializers

from layouts.models import Layout
from layouts.structs import LayoutData, PlacesData, DatesData, OutOfOrderPlacesData


class ShortLayoutDataSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=200)
    min_days = serializers.IntegerField(min_value=3, max_value=21)
    max_days = serializers.IntegerField(min_value=3, max_value=21)
    duration_limit = serializers.IntegerField(min_value=3, max_value=21)
    start_date = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=10)
    end_date = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=10)
    priorities = serializers.ListField(child=serializers.FloatField(min_value=0), required=False)
    update_from_file_date = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=10)

    def validate(self, data):
        return layout_data_validator(data)

    def create(self, validated_data):
        layout = Layout(name=validated_data.get('name'), min_days=validated_data.get('min_days'),
                        max_days=validated_data.get('max_days'), duration_limit=validated_data.get('duration_limit'))
        return layout, validated_data.get('priorities')


class OutOfOrderPlacesDataSerializer(serializers.Serializer):
    in_date = serializers.IntegerField(min_value=0)
    out_date = serializers.IntegerField(min_value=0)
    amount = serializers.IntegerField(min_value=0)
    auto_changed = serializers.BooleanField(default=False)


class PlacesDataSerializer(serializers.Serializer):
    in_date = serializers.IntegerField(min_value=0)
    out_date = serializers.IntegerField(min_value=0)
    amount = serializers.IntegerField(min_value=0)
    required = serializers.BooleanField()


class DatesDataSerializer(serializers.Serializer):
    in_date = serializers.CharField(max_length=10, allow_null=True)
    out_date = serializers.CharField(max_length=10, allow_null=True)
    in_amount = serializers.IntegerField(min_value=0, allow_null=True)
    in_losses = serializers.IntegerField(min_value=0, allow_null=True)
    out_amount = serializers.IntegerField(min_value=0, allow_null=True)
    out_losses = serializers.IntegerField(min_value=0, allow_null=True)
    in_no_losses = serializers.BooleanField(default=False)
    out_no_losses = serializers.BooleanField(default=False)
    priorities = serializers.ListField(child=serializers.FloatField(min_value=0), allow_null=True, min_length=1)


class FullLayoutDataSerializer(serializers.Serializer):
    id = serializers.IntegerField(min_value=1)
    name = serializers.CharField()
    width = serializers.IntegerField(min_value=1)
    min_days = serializers.IntegerField(min_value=3, max_value=21)
    max_days = serializers.IntegerField(min_value=3, max_value=21)
    duration_limit = serializers.IntegerField(min_value=3, max_value=21)
    priorities = serializers.ListField(child=serializers.FloatField(min_value=0))
    dates = serializers.ListField(child=DatesDataSerializer())
    places = serializers.ListField(child=PlacesDataSerializer())
    out_of_order = serializers.ListField(child=OutOfOrderPlacesDataSerializer(), allow_empty=True)
    update_from_file_date = serializers.CharField(allow_blank=True, allow_null=True, max_length=10)

    def validate(self, data):
        return layout_data_validator(data)

    def create(self, validated_data):
        places_data = validated_data.pop('places')
        dates_data = validated_data.pop('dates')
        out_of_order = validated_data.pop('out_of_order')
        places = [PlacesData(**pl_data) for pl_data in places_data]
        dates = [DatesData(**date_data) for date_data in dates_data]
        out_of_order = [OutOfOrderPlacesData(**ooo_data) for ooo_data in out_of_order]
        return LayoutData(validated_data.get('id'), validated_data.get('name'),
                          places, dates, validated_data.get('width'), validated_data.get('min_days'),
                          validated_data.get('max_days'), validated_data.get('priorities'), out_of_order,
                          validated_data.get('duration_limit'), validated_data.get('update_from_file_date'))


def layout_data_validator(data):
    if data['min_days'] > data['max_days']:
        raise serializers.ValidationError("Max days must be bigger than min days.")
    if data['max_days'] > data['duration_limit']:
        raise serializers.ValidationError("Duration limit must be bigger than max days.")
    if data['priorities'] is None:
        raise serializers.ValidationError("No priorities provided.")
    if len(data['priorities']) < data['max_days'] - data['min_days'] + 1:
        raise serializers.ValidationError("Some priorities were not provided.")
    return data
