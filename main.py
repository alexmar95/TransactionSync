import argparse
import json
import random
import rpyc
from rpyc.utils.server import ThreadedServer
from subprocess import Popen, PIPE
import threading

random.seed(42)


def merge_stdout(out):
    for line in out:
        print(line)


def main(args):
    with open(args.config) as f:
        config = json.load(f)

    processes = []
    port = 5000

    db_ports = []
    for _ in range(config["databases"]):
        p = Popen(["python.exe", "db.py", "--port", str(port)])
        processes.append(p)
        #threading.Thread(target=merge_stdout, args=(p.stdout, ))
        db_ports.append(port)
        port += 1

    for _ in range(config["routers"]):
        to = random.choice(db_ports)
        p = Popen(["python.exe", "router.py", "--port", str(port), "--database", str(to)])
        processes.append(p)
        #threading.Thread(target=merge_stdout, args=(p.stdout,))
        port+=1

    for p in processes:
        p.wait()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Whatever')
    parser.add_argument('--config', type=str, default='tata_lor.json')

    main(parser.parse_args())
