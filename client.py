import argparse
import json
import random
import time

from transaction import Transaction


class Client(object):
    def __init__(self, name):
        self.name = name

    def transact(self, to, value):
        t = Transaction(self.name, to, value)
        print(t)


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

    c = Client(args.name)
    while True:
        to = random.choice(friends)
        c.transact(to, random.randint(1, 15))
        time.sleep(3 + random.uniform(0, 2))
