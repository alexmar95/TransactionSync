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
    parser.add_argument('--name', '-n', type=str, help='Name to use', required=True)
    parser.add_argument('--config', type=str, default='tata_lor.json')
    args = parser.parse_args()

    config = json.load(open(args.config, 'r'))
    assert args.name in config["clients"], f"Unregistered name: {args.name}"

    friends = [f for f in config["clients"] if f != args.name]

    c = Client(args.name)
    while True:
        to = random.choice(friends)
        c.transact(to, random.randint(1, 15))
        time.sleep(3 + random.uniform(0, 2))