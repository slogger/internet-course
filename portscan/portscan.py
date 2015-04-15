from threading import Thread, active_count
import socket
import argparse
import sys
import csv

tcpports = []
udpports = []


def get_args():
    parser = argparse.ArgumentParser(description='portscan.py')
    parser.add_argument(
        'target',
        help='The target(s) you want to scan (192.168.0.1)')
    parser.add_argument(
        '-a', '--all',
        action='store_true',
        help='Enable this for full output')
    parser.add_argument(
        '-t', '--tcpscan',
        action='store_true',
        help='Enable this for TCP scans')
    parser.add_argument(
        '-p', '--ports',
        default='1-1024',
        help='The ports you want to scan (21,22,80,24-42)')
    parser.add_argument(
        '-m', '--multithreading',
        default=10,
        help='Thread count',
        type=int)
    return parser.parse_args()


def get_db():
    db = {
        'udp': {},
        'tcp': {}
    }
    with open('service-names-port-numbers.csv') as csv_file:
        data = csv.reader(csv_file)
        try:
            for rec in data:
                if rec[0] != 'Service Name':
                    try:
                        db[rec[2]].update({rec[1]: rec[0]})
                    except KeyError:
                        pass
        except UnicodeDecodeError:
            pass
    return db


def main():
    args = get_args()

    if args.ports == 'all':
        args.ports = '1-65535'

    ranges = (x.split("-") for x in args.ports.split(","))
    ports = [i for r in ranges for i in range(int(r[0]), int(r[-1]) + 1)]

    db = get_db()

    print(("Now scanning {}".format(args.target)))
    port_offset = len(ports) // args.multithreading
    for i in range(args.multithreading):
        t = Thread(
            target=portscan,
            args=(
                args.target,
                ports[port_offset*i:port_offset*(i+1)],
                args.tcpscan, args.all, db, ))
        t.start()


def portscan(target, ports, tcp, all, db):
    if tcp:
        for port in ports:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(1)
                s.connect((target, port))
            except Exception:
                if all:
                    print("{:0<5}/tcp \tclosed".format(port))
            else:
                try:
                    print("{}/tcp \t{} \topen".format(
                        port, db['tcp'][str(port)]))
                except KeyError:
                    print("{}/tcp \topen".format(port))
                tcpports.append(port)
            s.close()

if __name__ == '__main__':
    main()
