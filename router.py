import argparse
import rpyc
from rpyc.utils.server import ThreadedServer


class RouterService(rpyc.Service):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Start router')
    parser.add_argument('--number', '-n', type=int, help='Number of servers to start', default=1)
    args = parser.parse_args()

    for _ in range(args.number):
        server = ThreadedServer(RouterService, port=12345)
        server.start()
