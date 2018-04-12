import argparse
import random

import rpyc
from rpyc.utils.registry import TCPRegistryClient
from rpyc.utils.server import ThreadedServer


class Database(object):
    class __Database(object):
        # Thread-safe operations:
        # -reading or replacing a single instance attribute
        # -fetching an item from a list
        # -modifying a list in place(e.g.adding an item using append)
        # -fetching an item from a dictionary
        # -modifying a dictionary in place(e.g.adding an item, or calling the clear method)

        def __init__(self):
            self.record = []
            self.fail_rate = 0.
            self.registrar = TCPRegistryClient("localhost")

    instance = None

    def __new__(cls):
        if not Database.instance:
            Database.instance = Database.__Database()
        return Database.instance

    def __getattr__(self, name):
        return getattr(self.instance, name)

    def __setattr__(self, name):
        return setattr(self.instance, name)

    @staticmethod
    def load_with(fail_rate):
        Database().fail_rate = fail_rate


class DatabaseService(rpyc.Service):
    ALIASES = ["DB"]

    def exposed_coordinate_transaction(self, transaction):
        record = Database().record
        record.append(transaction)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Whatever')
    parser.add_argument('--port', '-p', type=int, help='Port to use', default=12345)
    parser.add_argument('--id', '-i', type=int, help='Unique number from 1-DB_count and the DB_count',
                        default=[0, 1], nargs=2)
    parser.add_argument('--seed', '-s', type=int, help='RNG seed', default=42)
    args = parser.parse_args()

    random.seed(args.seed)

    Database.load_with(random.uniform(.25, .5))
    server = ThreadedServer(DatabaseService, port=args.port, registrar=Database().registrar)
    print('Starting DatabaseService(id: %d/%d) on port %d with failure rate %f'
          % (*args.id, args.port, Database().fail_rate))
    server.start()
