import argparse
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

    instance = None

    def __new__(cls):
        if not Database.instance:
            Database.instance = Database.__Database()
        return Database.instance

    def __getattr__(self, name):
        return getattr(self.instance, name)

    def __setattr__(self, name):
        return setattr(self.instance, name)


class DatabaseService(rpyc.Service):
    ALIASES = ["DB"]

    def exposed_register_transaction(self, transaction):
        record = Database().record
        record.append(transaction)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Whatever')
    parser.add_argument('--port', '-p', type=int, help='Port to use', default=12345)
    args = parser.parse_args()

    print('Sanity check DB')

    server = ThreadedServer(DatabaseService, port=args.port, registrar=TCPRegistryClient("localhost"))
    server.start()
