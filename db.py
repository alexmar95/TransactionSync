import argparse
import rpyc
from rpyc.utils.server import ThreadedServer


class DatabaseService(rpyc.Service):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.t_log = []

    def exposed_register_transaction(self, transaction):
        self.t_log.append(transaction)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Whatever')
    parser.add_argument('--number', '-n', type=int, help='Number of servers to start', default=1)
    args = parser.parse_args()

    for _ in range(args.number):
        server = ThreadedServer(DatabaseService, port=12345)
        server.start()
