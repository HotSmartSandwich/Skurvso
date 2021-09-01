from rest_framework import serializers

from Dispatcher.models import Unit


class UnitModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = ('id', 'host', 'port')
