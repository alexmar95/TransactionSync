import argparse
import rpyc
from rpyc.utils.server import ThreadedServer
import sys


def classpartial(*args, **kwargs):
    """Bind arguments to a class's __init__."""
    cls, args = args[0], args[1:]
    class Partial(cls):
        __doc__ = cls.__doc__
        def __new__(self):
            return cls(*args, **kwargs)
    Partial.__name__ = cls.__name__
    return Partial


class RouterService(rpyc.Service):
    def __init__(self, db_port, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.db_node = rpyc.connect("localhost", db_port)
        print('Connected to %d' % self.db_port)
        self.db_node.register_transaction(str(db_port) + " ciuciu")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Start router')
    parser.add_argument('--port', '-p', type=int, help='Connection port', default=1)
    parser.add_argument('--database', '-d', type=int, help='Database Service port')
    args = parser.parse_args()

    service = classpartial(RouterService, args.database)
    with open('Rout_%d' % args.port, 'w') as f:
        sys.stdout = f
        server = ThreadedServer(service, port=args.port)
        server.start()
