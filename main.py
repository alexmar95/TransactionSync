import argparse
import rpyc


def main(args):
    pass

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Whatever')
    parser.add_argument('--databases', '-d', type=int, help='Number of databases to start', default=1)
    parser.add_argument('--routers', '-s', type=int, help='Number of routers to start', default=1)

    main(parser.parse_args())