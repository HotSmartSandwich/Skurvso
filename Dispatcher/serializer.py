from rest_framework import serializers

from Dispatcher.models import Measurement


class MeasurementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Measurement
        fields = ('time', 'value')
