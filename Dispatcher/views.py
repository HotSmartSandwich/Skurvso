import datetime

from django.shortcuts import render
from django.utils import timezone

from Dispatcher.models import Node, Building, Unit, Measurement

TZ = timezone.get_default_timezone()


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


def unit_page(request, unit_id, start_datetime=None, end_datetime=None):
    start_datetime = start_datetime or datetime.datetime.combine(datetime.date.today(), datetime.time(7, 30), TZ)
    end_datetime = end_datetime or datetime.datetime.combine(datetime.date.today(), datetime.time(17, 30), TZ)

    unit = Unit.objects.get(id=unit_id)

    labels = []
    data = []

    measurements = Measurement.objects.filter(unit_id=unit_id, time__gte=start_datetime, time__lte=end_datetime)[:10]

    for measurement in measurements:
        labels.append(measurement.time.astimezone(TZ).strftime('%H:%M:%S'))
        data.append(measurement.value)

    return render(request, 'unit_page.html', {'unit': unit, 'labels': labels, 'data': data, })
