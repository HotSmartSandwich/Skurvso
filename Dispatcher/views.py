from datetime import date, time, datetime

from django.http import QueryDict
from django.shortcuts import render
from django.utils import timezone
from rest_framework import generics

from Dispatcher.models import Node, Building, Unit, Measurement
from Dispatcher.serializer import MeasurementSerializer

TZ = timezone.get_current_timezone()


def main_page(request):
    buildings = Building.objects.all()
    return render(request, 'main_page.html', {'buildings': buildings})


def building_page(request, building_id):
    building = Building.objects.get(id=building_id)
    nodes = Node.objects.filter(building_id=building_id)
    return render(request, 'building_page.html', {'building': building, 'nodes': nodes})


def node_page(request, node_id):
    node = Node.objects.get(id=node_id)
    units = Unit.objects.filter(node_id=node_id)
    return render(request, 'node_page.html', {'node': node, 'units': units})


START_TIME = time(7, 30)
END_TIME = time(17, 30)
POINTS_NUMBER = 250


def unit_page(request, unit_id):
    unit = Unit.objects.get(id=unit_id)
    start_date = date.today().isoformat()
    start_time = START_TIME.isoformat()
    end_time = END_TIME.isoformat()
    points_number = POINTS_NUMBER
    return render(request, 'unit_page.html', {'unit': unit,
                                              'start_date': start_date,
                                              'start_time': start_time,
                                              'end_time': end_time,
                                              'points_number': points_number})


class MeasurementsList(generics.ListAPIView):
    serializer_class = MeasurementSerializer

    def get_queryset(self):
        request_query: QueryDict = self.request.query_params

        unit_id = request_query.get('unit_id')
        start_date = request_query.get('start_date')
        start_time = request_query.get('start_time')
        end_time = request_query.get('end_time')
        points_number = int(request_query.get('points_number', POINTS_NUMBER))

        start_date = date.fromisoformat(start_date) if start_date else date.today()
        start_time = time.fromisoformat(start_time) if start_time else START_TIME
        end_time = time.fromisoformat(end_time) if end_time else END_TIME

        start_datetime = TZ.localize(datetime.combine(start_date, start_time))
        end_datetime = TZ.localize(datetime.combine(start_date, end_time))

        query = Measurement.objects.filter(unit_id=unit_id,
                                           time__gte=start_datetime,
                                           time__lte=end_datetime)
        query_step = round(query.count() / points_number) or 1
        return query[::query_step]
