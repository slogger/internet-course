import socket
import argparse
import sys


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
    return parser.parse_args()


def main():
    args = get_args()

    if args.ports == 'all':
        args.ports = '1-65535'

    ranges = (x.split("-") for x in args.ports.split(","))
    ports = [i for r in ranges for i in range(int(r[0]), int(r[-1]) + 1)]

    db = get_db()

    tcpports = portscan(
        args.target, ports, args.tcpscan, args.all, db)


def portscan(target, ports, tcp, all, db):
    print(("Now scanning %s" % (target)))
    tcpports = []
    udpports = []
    if tcp:
        for portnum in ports:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(1)
                s.connect((target, portnum))
            except Exception:
                failvar = 0
                if all:
                    print("{:0<5}/tcp \tclosed".format(portnum))
            else:
                print("{}/tcp \topen".format(portnum))
                tcpports.append(portnum)
            s.close()
    return tcpports

if __name__ == '__main__':
    main()
