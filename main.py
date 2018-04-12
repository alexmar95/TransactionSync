import argparse
import json
import os
import random
from subprocess import Popen

random.seed(42)


def spawn_registry(log_to):
    r_log = open(os.path.join(log_to, 'Registry.log'), 'w')
    for p in os.environ["PATH"].split(';'):
        registry_path = os.path.join(p, "rpyc_registry.py")
        if os.path.exists(registry_path):
            try:
                processes = [Popen(["python.exe", registry_path, "--mode", "TCP"], stderr=r_log)]
            except FileNotFoundError:
                pass
            else:
                return processes


def main(args):
    with open(args.config) as f:
        config = json.load(f)

    processes = spawn_registry(args.logdir)
    assert processes, "Unable to spawn registry"

    port = 5000

    db_ports = []
    for _ in range(config["databases"]):
        log_file = open(os.path.join(args.logdir, 'DB_%d.log' % port), 'w')
        p = Popen(["python.exe", "db.py", "--port", str(port)], stderr=log_file)
        processes.append(p)
        db_ports.append(port)
        port += 1

    for _ in range(config["routers"]):
        to = random.choice(db_ports)
        log_file = open(os.path.join(args.logdir, 'Router_%d.log' % port), 'w')
        p = Popen(["python.exe", "router.py", "--port", str(port), "--database", str(to)], stderr=log_file)
        processes.append(p)
        port += 1

    for p in processes:
        p.wait()
    else:
        print("The young perish and the old linger. That I should live to see the last days of my house")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Whatever')
    parser.add_argument('--config', type=str, default='tata_lor.json')
    parser.add_argument('--logdir', type=str, default='logs')

    main(parser.parse_args())
