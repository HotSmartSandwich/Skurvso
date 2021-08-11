from datetime import date, time, datetime

from django.shortcuts import render
from django.utils import timezone
from rest_framework import views
from rest_framework.request import Request
from rest_framework.response import Response

from Dispatcher.models import Node, Building, Unit, Measurement

TZ = timezone.get_current_timezone()
START_TIME = time(7, 30)
END_TIME = time(17, 30)
POINTS_NUMBER = 250


def get_context(building_id=None, node_id=None, unit_id=None):
    context = dict()
    if unit_id is not None:
        context = {
            'start_date': date.today().isoformat(),
            'start_time': START_TIME.isoformat(),
            'end_time': END_TIME.isoformat(),
            'points_number': POINTS_NUMBER
        }

        unit = Unit.objects.get(id=unit_id)
        context['unit'] = unit
        node_id = unit.node_id
    if node_id is not None:
        node = Node.objects.get(id=node_id)
        units = Unit.objects.filter(node=node)
        context['node'] = node
        context['units'] = units
        building_id = node.building_id
    if building_id is not None:
        building = Building.objects.get(id=building_id)
        nodes = Node.objects.filter(building=building)
        context['building'] = building
        context['nodes'] = nodes
    return context


def main_page(request):
    return render(request, 'main_page.html')


def building_page(request, building_id):
    context = get_context(building_id=building_id)
    return render(request, 'building_page.html', context)


def node_page(request, node_id):
    context = get_context(node_id=node_id)
    return render(request, 'node_page.html', context)


def unit_page(request, unit_id):
    context = get_context(unit_id=unit_id)
    return render(request, 'unit_page.html', context)


class MeasurementsList(views.APIView):
    def get(self, request: Request):
        request_params = request.query_params

        unit_id = request_params.get('unit_id')
        start_date = request_params.get('start_date')
        start_time = request_params.get('start_time')
        end_time = request_params.get('end_time')
        points_number = int(request_params.get('points_number', POINTS_NUMBER))

        start_date = date.fromisoformat(start_date) if start_date else date.today()
        start_time = time.fromisoformat(start_time) if start_time else START_TIME
        end_time = time.fromisoformat(end_time) if end_time else END_TIME

        start_datetime = TZ.localize(datetime.combine(start_date, start_time))
        end_datetime = TZ.localize(datetime.combine(start_date, end_time))

        query_filter = dict(unit_id=unit_id, time__gte=start_datetime, time__lte=end_datetime)

        all_measurements = Measurement.objects.filter(**query_filter, value__isnull=False).order_by('time')

        try:
            step = round(all_measurements.count() / points_number) or 1
        except ZeroDivisionError:
            return

        measurement_ids = [measurement.id for measurement in all_measurements][::step]
        try:
            last_measurement = all_measurements.latest()
        except Measurement.DoesNotExist:
            return
        measurement_ids.append(last_measurement.id)

        breaks = Measurement.objects.filter(**query_filter, value__isnull=True)
        measurement_ids += [measurement.id for measurement in breaks]

        response = Measurement.objects.filter(id__in=measurement_ids).order_by('time')
        response = map(lambda m: dict(x=m.time, y=m.value), response)

        return Response(response)
