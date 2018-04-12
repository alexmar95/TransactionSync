import argparse
import rpyc

from rpyc.utils.registry import TCPRegistryClient
from rpyc.utils.server import ThreadedServer


class RouterService(rpyc.Service):

    def on_connect(self):
        print('Connecting to %d' % args.database)
        self.db_node = rpyc.connect("", args.database)
        self.db_node.root.register_transaction(str(args.database) + " ciuciu")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Start router')
    parser.add_argument('--port', '-p', type=int, help='Connection port', default=1)
    parser.add_argument('--database', '-d', type=int, help='Database Service port')
    args = parser.parse_args()

    print('Sanity check Router')

    server = ThreadedServer(RouterService, port=args.port, registrar=TCPRegistryClient("localhost"))
    server.start()
