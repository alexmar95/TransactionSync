import argparse
import random
from threading import Timer

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
            self.id = 0
            self.fail_rate = 0.
            self.port = 12345

            self.registrar = TCPRegistryClient("localhost")
            self.record = []
            self.pending_transactions = {}

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
    def load_with(id, port, fail_rate):
        d = Database()
        d.id, d.port, d.fail_rate = id, port, fail_rate


class DatabaseService(rpyc.Service):
    ALIASES = ["DB"]

    def exposed_transaction_request(self, transaction):
        print("DB-%d: %s requested" % (Database().id, hash(transaction)))
        if self.check_valid(transaction):
            r = Database().prending_transactions
            r[transaction] = {}
        else:
            return False

        threads = []
        for addr, port in Database().registrar.discover("DB"):
            if port != Database().port:
                r[transaction][addr, port] = False
                threads.append(Timer(1., self.can_commit, args=((addr, port), transaction)))
                threads[-1].start()

        for t in threads:
            t.join()

        if all(Database().pending_transactions[transaction].values()):
            pass
        else:
            return False

    def can_commit(self, cohort, transaction):
        addr, port = cohort
        conn = rpyc.connect(addr, port)
        if conn.root.vote_for(transaction):
            Database().pending_transactions[transaction][cohort] = True

    def exposed_vote_for(self, transaction):
        if self.check_valid(transaction):
            return True
        else:
            return False

    def check_valid(self, transaction):
        return True

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Whatever')
    parser.add_argument('--port', '-p', type=int, help='Port to use', default=12345)
    parser.add_argument('--id', '-i', type=int, help='Unique number from 1-DB_count and the DB_count',
                        default=[0, 1], nargs=2)
    parser.add_argument('--seed', '-s', type=int, help='RNG seed', default=42)
    args = parser.parse_args()

    random.seed(args.seed)

    Database.load_with(args.id, args.port, random.uniform(.0, .2))
    server = ThreadedServer(DatabaseService, port=args.port, registrar=Database().registrar)
    print('Starting DatabaseService(id: %d/%d) on port %d with failure rate %f'
          % (args.id[0], args.id[1], args.port, Database().fail_rate))
    server.start()
