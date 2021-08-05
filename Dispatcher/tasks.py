import time

from celery.signals import worker_ready

from Dispatcher.models import Node
from Dispatcher.node_communicator import NodeCommunicator, CommunicatorException
from Skurvso.celery import app


@worker_ready.connect
def run(sender, **kwargs):
    nodes = Node.objects.all()
    with sender.app.connection() as conn:
        for node in nodes:
            sender.app.send_task('handle_node', args=(node.id,), connection=conn)


@app.task(name='handle_node')
def handle_node(node_id, time_interval=1):
    node = Node.objects.get(id=node_id)
    node_communicator = NodeCommunicator(node)

    while True:
        try:
            node_communicator.connect()
        except CommunicatorException as e:
            print_exception(node, e)
            time.sleep(10)
            continue

        while True:
            time.sleep(time_interval - time.time() % time_interval + 0.2)

            try:
                node_communicator.handle_measurements()
                node_communicator.handle_states()
            except CommunicatorException as e:
                print_exception(node, e)
                time.sleep(10)
                break


def print_exception(node: Node, e: CommunicatorException):
    print(f'{node.host:<15}: {e}')
