from datetime import datetime, timedelta
from json import JSONDecodeError

import ntplib
import requests
from django.db import IntegrityError
from django.utils import timezone
from requests.exceptions import ConnectionError, ConnectTimeout

from Dispatcher.models import Node, Unit, Measurement

TZ = timezone.get_default_timezone()


class CommunicatorException(BaseException):
    pass


class NodeCommunicator:
    _node_time_key: str
    _node_time_delta: float

    def __init__(self, node: Node):
        self._node_id = node.id
        base_url = f'http://{node.host}:{node.port}/skurvso/api'
        self._ntp_server_url = node.host
        self._units_url = base_url + '/units'
        self._time_key_url = base_url + '/time_key'
        self._measurements_url = base_url + '/measurements'
        self._states_url = base_url + '/states'

    def connect(self) -> None:
        self._node_time_key = self._get_time_key()
        self._node_time_delta = self._get_time_delta()
        if self._node_time_key != self._get_time_key():
            raise CommunicatorException('connect: time_key validation error')

    def update_unit_list(self) -> None:
        node_units: list[dict] = self.request('get', self._units_url)
        node_units: dict[int, dict] = {unit.get('id'): unit for unit in node_units}

        reboot_required = False
        for unit in Unit.objects.filter(node_id=self._node_id):
            if unit.id in node_units:
                if unit.host == node_units.get(unit.id).get('host'):
                    node_units.pop(unit.id)
                else:
                    self._post_unit(unit)
                    reboot_required = True
            else:
                self._put_unit(unit)
                reboot_required = True

        for unit in node_units:
            self._delete_unit(unit)
            reboot_required = True

        if reboot_required:
            self.reboot_node()

    def _get_time_key(self) -> str:
        response: dict = self.request('get', self._time_key_url)
        return response.get('time_key')

    def _get_time_delta(self) -> float:
        ntp_client = ntplib.NTPClient()
        try:
            response = ntp_client.request(self._ntp_server_url, version=3, timeout=1)
        except ntplib.NTPException as e:
            raise CommunicatorException(f'get_time_delta: {e}')
        return -response.offset

    def handle_measurements(self) -> None:
        self._handle_records(self._measurements_url, Measurement)

    def handle_states(self) -> None:
        # self._handle_records(self._measurements_url, State)
        pass

    def _handle_records(self, records_url, db_model) -> None:
        records: list = self.request('get', records_url, params={'time_key': self._node_time_key}, timeout=10)

        if not records:
            return

        sorted(records, key=lambda u: u.get('id'))
        start_id = records[0].get('id')
        end_id = records[-1].get('id')

        for record in records:
            record.pop('id')
            record['time'] = datetime.fromtimestamp(record.pop('timestamp') + self._node_time_delta, tz=TZ)
            new_db_record = db_model(**record)

            try:
                latest_db_record = db_model.objects.filter(unit=new_db_record.unit).latest()
            except Measurement.DoesNotExist:
                pass
            else:
                if new_db_record.time - latest_db_record.time >= timedelta(seconds=5):
                    Measurement(unit=new_db_record.unit, time=latest_db_record.time + timedelta(seconds=1)).save()

            try:
                new_db_record.save()
            except IntegrityError as e:
                print(e)

        requests.delete(records_url, params={'time_key': self._node_time_key,
                                             'start_id': start_id,
                                             'end_id': end_id})

    @staticmethod
    def request(request_type: str, url: str, params: dict = None, data: dict = None, timeout: int = 5):
        try:
            response = requests.request(request_type, url, params=params, json=data, timeout=timeout)
        except (ConnectionRefusedError, ConnectionError, ConnectTimeout) as e:
            raise CommunicatorException(f'{url}: {e}')
        try:
            return response.json()
        except JSONDecodeError:
            raise CommunicatorException(f'{url}: JSON decode error')

    def _post_unit(self, unit):
        response = self.request('post', self._units_url, unit, timeout=5)
        if response != unit:
            pass

    def _put_unit(self, unit):
        response = self.request('put', self._units_url, unit, timeout=5)
        if unit != response:
            pass

    def _delete_unit(self, unit):
        response = self.request('delete', self._units_url, unit, timeout=5)
        if unit != response:
            pass

    def reboot_node(self):
        pass
