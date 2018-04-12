import argparse
import random

import rpyc
from rpyc.utils.registry import TCPRegistryClient
from rpyc.utils.server import ThreadedServer


cfg = {
    "registrar": TCPRegistryClient("localhost"),
    "database": 12345
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

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Start router')
    parser.add_argument('--port', '-p', type=int, help='Connection port', default=23456)
    parser.add_argument('--database', '-d', type=int, help='Database Service port', default=12345)
    parser.add_argument('--seed', '-s', type=int, help='RNG seed', default=42)
    args = parser.parse_args()

    random.seed(args.seed)
    cfg["database"] = args.database

    server = ThreadedServer(RouterService, port=args.port, registrar=cfg["registrar"])
    print('Starting RouterService on port %d coordinating through port %d' % (args.port, args.database))
    server.start()

