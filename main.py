import argparse
import json
import os
import random
from subprocess import Popen
import sys

from rpyc.utils.registry import TCPRegistryClient


def spawn_registry(log_to):
    r_log = open(os.path.join(log_to, 'Registry.log'), 'w')
    for p in os.environ["PATH"].replace(':', ';').split(';'):
        registry_path = os.path.join(p, "rpyc_registry.py")
        if os.path.exists(registry_path):
            try:
                processes = [Popen(["python", registry_path, "--mode", "TCP"], stderr=r_log)]
            except OSError:
                pass
            else:
                return processes
    else:
        return [Popen(["python", 'rpyc_registry.py', "--mode", "TCP"], stderr=r_log)]


def main(args):
    if args.seed:
        random.seed(args.seed)

    with open(args.config) as f:
        config = json.load(f)

    if args.registrar == 'localhost':
        processes = spawn_registry(args.logdir)
        assert processes, "Unable to spawn registry"
    else:
        processes = []

    port = 5000

    db_ports = []
    for i in range(config["databases"]):
        log_file = open(os.path.join(args.logdir, 'DB_%d.log' % port), 'w')
        p = Popen(["python", "db.py", "-p", str(port), '-i', str(i), str(config["databases"]), '-s', str(args.seed+i), '-r', args.registrar],
                  stderr=log_file)
        processes.append(p)
        db_ports.append(port)
        port += 1

    for i in range(config["routers"]):
        to = random.choice(db_ports)
        log_file = open(os.path.join(args.logdir, 'Router_%d.log' % port), 'w')
        p = Popen(["python", "router.py", "-p", str(port), "-d", "localhost", str(to), '-s', str(args.seed + i), '-r', args.registrar], stderr=log_file)
        processes.append(p)
        port += 1

    for i, name in enumerate(config["clients"]):
        log_file = open(os.path.join(args.logdir, 'Client_%d.log' % port), 'w')
        p = Popen(["python", "client.py", "-n", name, '-s', str(args.seed + i), '-r', args.registrar], stderr=log_file)
        processes.append(p)
        port += 1

    for p in processes:
        p.wait()
    else:
        print("The young perish and the old linger. That I should live to see the last days of my house.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Whatever')
    parser.add_argument('--config', type=str, default='tata_lor.json')
    parser.add_argument('--logdir', type=str, default='logs')
    parser.add_argument('--seed', '-s', type=int, default=42)
    parser.add_argument('--registrar', '-r', type=str, help='Registrar address', default='localhost')

    main(parser.parse_args())
