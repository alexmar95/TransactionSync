import argparse
import random

import rpyc
from rpyc.utils.registry import TCPRegistryClient
from rpyc.utils.server import ThreadedServer
rpyc.core.protocol.DEFAULT_CONFIG['allow_pickle'] = True


cfg = {
    "registrar": TCPRegistryClient("localhost"),
    "database": ("localhost", 12345)
}


class RouterService(rpyc.Service):

    def on_connect(self):
        found = cfg["registrar"].discover("DB")
        for addr, p in found:
            if p == cfg["database"]:
                self.db_node = rpyc.connect(addr, p)
                break
        else:
            raise RuntimeError('No databases found with port %d' % cfg["database"])

    def on_disconnect(self):
        self.db_node = None

    def exposed_transaction_request(self, transaction):
        return self.db_node.root.transaction_request(transaction)

    def exposed_balance_check(self, name):
        return self.db_node.root.balance_check()[name]

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Start router')
    parser.add_argument('--port', '-p', type=int, help='Connection port', default=23456)
    parser.add_argument('--database', '-d', type=str, nargs=2, help='Database Service port', default=["localhost", "12345"])
    parser.add_argument('--seed', '-s', type=int, help='RNG seed', default=42)
    parser.add_argument('--registrar', '-r', type=str, help='Registrar address', default='localhost')
    args = parser.parse_args()

    random.seed(args.seed)
    cfg["database"] = args.database
    cfg["database"][1] = int(cfg["database"][1])
    cfg["registrar"] = TCPRegistryClient(args.registrar)

    server = ThreadedServer(RouterService, port=args.port, registrar=cfg["registrar"])
    print('Starting RouterService on port %d coordinating through port %d' % (args.port, args.database))
    server.start()

