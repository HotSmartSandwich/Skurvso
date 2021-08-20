from datetime import date, time, datetime

from django.shortcuts import render
from django.utils import timezone
from rest_framework import views
from rest_framework.request import Request
from rest_framework.response import Response

from Dispatcher.models import Node, Building, Unit, Measurement

TZ = timezone.get_current_timezone()


def get_context(building_id=None, node_id=None, unit_id=None):
    context = dict()
    if unit_id is not None:
        context = {
            'start_date': date.today().isoformat(),
            'start_time': time(7, 30).isoformat(),
            'end_time': time(17, 30).isoformat(),
            'points_number': 250
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

        unit_id = request_params.get('unitId')
        start_date = date.fromisoformat(request_params.get('startDate'))
        start_time = time.fromisoformat(request_params.get('startTime') or '00:00')
        end_time = time.fromisoformat(request_params.get('endTime') or '23:59:59')
        points_number = abs(int(request_params.get('pointsNumber') or 0))

        start_datetime = TZ.localize(datetime.combine(start_date, start_time))
        end_datetime = TZ.localize(datetime.combine(start_date, end_time))

        query_filter = dict(unit_id=unit_id, time__gte=start_datetime, time__lte=end_datetime)
        query = Measurement.objects.filter(**query_filter, value__isnull=False).order_by('time')

        try:
            latest_measurement = query.latest()
        except Measurement.DoesNotExist:
            return Response()

        try:
            step = round(query.count() / points_number)
        except ZeroDivisionError:
            step = 0
        if step > 1:
            query_sliced: list[Measurement] = query[::step]
        else:
            query_sliced: list[Measurement] = list(query)

        query_sliced.append(latest_measurement)

        break_points: list[Measurement] = list(Measurement.objects.filter(**query_filter, value__isnull=True))
        response = sorted(query_sliced + break_points, key=lambda meas: meas.time)

        return Response(map(serialize, response))


def serialize(measurement: Measurement):
    return dict(x=measurement.time, y=measurement.value)
