import argparse
import rpyc
from rpyc.utils.server import ThreadedServer
import sys


class DatabaseService(rpyc.Service):
    ALIASES = ["DB"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.t_log = []

    def exposed_register_transaction(self, transaction):
        self.t_log.append(transaction)
        print(transaction)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Whatever')
    parser.add_argument('--port', '-p', type=int, help='Port to use')
    args = parser.parse_args()

    with open('caca/DB%d' % args.port, 'w') as f:
        sys.stdout = f
        server = ThreadedServer(DatabaseService, port=args.port)
        server.start()
