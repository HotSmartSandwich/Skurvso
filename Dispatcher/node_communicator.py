from datetime import datetime

import ntplib
import requests
from django.db import IntegrityError
from django.utils import timezone
from requests.exceptions import ConnectionError, ConnectTimeout

from Dispatcher.models import Node, Measurement

TZ = timezone.get_default_timezone()


class CommunicatorException(BaseException):
    pass


class NodeCommunicator:
    _node_time_key: str
    _node_time_delta: float

    def __init__(self, node: Node):
        base_url = f'http://{node.host}:{48621}/skurvso/api'
        self._ntp_server_url = node.host
        self._time_key_url = base_url + '/time_key'
        self._measurements_url = base_url + '/measurements'
        self._states_url = base_url + '/states'

        self._node_id = node.id

    def connect(self):
        self._node_time_key = self._get_time_key()
        self._node_time_delta = self._get_time_delta()
        if self._node_time_key != self._get_time_key():
            raise CommunicatorException('connect: time_key validation error')

    def _get_time_key(self) -> str:
        try:
            response = requests.get(self._time_key_url, timeout=5)
        except (ConnectionRefusedError, ConnectionError, ConnectTimeout) as e:
            raise CommunicatorException(f'get_time_key: {e}')

        if response.status_code == 200:
            return response.json().get('time_key')
        else:
            raise CommunicatorException(f'get_time_key: {response.status_code = }')

    def _get_time_delta(self) -> float:
        return 0  # DEBUG
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
        try:
            response = requests.get(records_url, params={'time_key': self._node_time_key}, timeout=10)
        except (ConnectionRefusedError, ConnectionError, ConnectTimeout) as e:
            raise CommunicatorException(f'get_time_key: {e}')
        if response.status_code == 200:
            records = response.json()
        else:
            raise CommunicatorException(f'get_time_key: {response.status_code = }')

        if not records:
            return

        start_id = records[0].get('id')
        end_id = records[-1].get('id')
        for record in records:
            record.pop('id')
            record['time'] = datetime.fromtimestamp(record.pop('timestamp'), tz=TZ)
            db_record = db_model(**record)
            try:
                db_record.save()
                print(record.get('time'), record.get('value'))
            except IntegrityError as e:
                print(e)

        response = requests.delete(records_url, params={'time_key': self._node_time_key,
                                                        'start_id': start_id,
                                                        'end_id': end_id})
        if response.status_code != 200:
            raise CommunicatorException(f'get_time_key: {response.status_code = }')
