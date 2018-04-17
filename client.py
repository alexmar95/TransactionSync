import argparse
import json
import random
import time

import rpyc
from rpyc.utils.registry import TCPRegistryClient
rpyc.core.protocol.DEFAULT_CONFIG['allow_pickle'] = True

from transaction import Transaction


class Client(object):
    def __init__(self, name, registrar):
        self.name = name
        self.registrar = registrar

    def transact(self, to, value):
        t = Transaction(self.name, to, value)
        router = self.get_closest_router()

        me, it = router.root.balance_check(self.name), router.root.balance_check(to)
        print("I(%s) had %d and %s had %d." % (self.name, me, to, it))
        if router.root.transaction_request(t):
            print("I(%s) now have %d and %s has %d." %
                  (self.name, router.root.balance_check(self.name), to, router.root.balance_check(to)))
        else:
            print('%s be salty!' % self.name)

    def get_closest_router(self):
        l = self.registrar.discover("Router")
        addr, port = random.choice(l)
        return rpyc.connect(addr, port)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Starts a client')
    parser.add_argument('--config', type=str, default='tata_lor.json')
    parser.add_argument('--name', '-n', type=str, help='Name to use', required=True)
    parser.add_argument('--seed', '-s', type=int, help='RNG seed', default=42)

    args = parser.parse_args()

    print('Sanity check Client')
    random.seed(args.seed)

    config = json.load(open(args.config, 'r'))
    assert args.name in config["clients"], "Unregistered name: %s" % args.name

    friends = [f for f in config["clients"] if f != args.name]

    c = Client(args.name, TCPRegistryClient("localhost"))
    while True:
        time.sleep(random.uniform(3, 5))
        to = random.choice(friends)
        c.transact(to, random.randint(1, 15))
