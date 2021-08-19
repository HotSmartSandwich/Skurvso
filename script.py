import time
from datetime import datetime
from random import random

from django.utils import timezone

from Dispatcher.models import Measurement


def main():
    tz = timezone.get_current_timezone()
    time_interval = 1
    amplitude = 100
    value: float = 0
    while True:
        time.sleep(time_interval - time.time() % time_interval + 0.2)
        value += (2 * amplitude) * random() - 100
        if value < 0:
            value = 0
        Measurement(unit_id=8, time=datetime.now(tz), value=value).save()


if __name__ == '__main__':
    main()
