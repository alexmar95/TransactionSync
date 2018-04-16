import argparse
import json
import pickle
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
            self.record = {}
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
    def load_with(id, port, fail_rate, cfg):
        d = Database()
        with open(cfg, 'r') as f:
            clients = json.load(f)['clients']

        d.record = {name: balance for name, balance in clients.items()}
        d.id, d.port, d.fail_rate = id, port, fail_rate


class DatabaseService(rpyc.Service):
    ALIASES = ["DB"]

    def exposed_transaction_request(self, transaction):
        print("DB-%s: %s requested" % (str(Database().id), transaction))
        if self.check_valid(transaction):
            r = Database().pending_transactions
            r[transaction] = {}
        else:
            return False

        threads = []
        for addr, port in Database().registrar.discover("DB"):
            if port != Database().port:
                r[transaction][addr, port] = False
                threads.append(Timer(random.uniform(1., 5.), self.can_commit, args=((addr, port), transaction)))
                threads[-1].start()

        for t in threads:
            t.join()

        if all(r[transaction].values()):
            for addr, port in r[transaction]:
                rpyc.connect(addr, port).root.complete_transaction(transaction)
            else:
                self.exposed_complete_transaction(transaction)
            return True
        else:
            return False

    def can_commit(self, cohort, transaction):
        addr, port = cohort
        print('Can %d commit to transaction' % port)
        conn = rpyc.connect(addr, port)
        if conn.root.vote_for(transaction):
            Database().pending_transactions[transaction][cohort] = True

    def exposed_vote_for(self, transaction):
        if self.check_valid(transaction):
            print('DB-%s: Sigur, unde semnez?' % str(Database().id))
            return True
        else:
            return False

    def check_valid(self, transaction):
        rec = Database().record
        return rec[transaction.src] >= transaction.value >= 0

    def exposed_complete_transaction(self, transaction):
        d = Database()
        d.pending_transactions.pop(transaction, None)
        d.record[transaction.src] -= transaction.value
        d.record[transaction.dst] += transaction.value

    def exposed_balance_check(self):
        return Database().record

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Whatever')
    parser.add_argument('--port', '-p', type=int, help='Port to use', default=12345)
    parser.add_argument('--id', '-i', type=int, help='Unique number from 1-DB_count and the DB_count',
                        default=[0, 1], nargs=2)
    parser.add_argument('--seed', '-s', type=int, help='RNG seed', default=42)
    parser.add_argument('--config', '-c', type=str, help='config file', default='tata_lor.json')
    args = parser.parse_args()

    random.seed(args.seed)

    Database.load_with(args.id, args.port, random.uniform(.0, .2), args.config)
    server = ThreadedServer(DatabaseService, port=args.port, registrar=Database().registrar)
    print('Starting DatabaseService(id: %d/%d) on port %d with failure rate %f'
          % (args.id[0], args.id[1], args.port, Database().fail_rate))
    server.start()
