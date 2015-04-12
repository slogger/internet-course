#!/usr/bin/python3

import argparse
from time import time
from random import randint
import socket
from struct import pack, unpack
import asyncio
from common import *


class NTPServer(asyncio.Protocol):
    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        packet = packet_from_binary(data)
        packet.receive_binary = utc_to_ntp_bytes(time())
        packet.stratum = 2
        packet.options = 36
        packet.precision_binary = randint(0, 256)
        packet.ref_id_binary = get_my_ip()
        packet.origin_binary = utc_to_ntp_bytes(time() + (args.delay * 2))
        packet.ref_time_binary = utc_to_ntp_bytes(time())
        r = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        r.connect(addr)
        packet = packet.to_binary()
        self.transport.sendto(packet, addr)


def get_args_parser():
    parser = argparse.ArgumentParser(description="NTP Server")
    parser.add_argument(
        "--delay",
        help="Set delay",
        type=int,
        default=0)
    parser.add_argument(
        "-p", "--port",
        help="port",
        type=int,
        default=5000)
    return parser


def get_my_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('urfu.ru', 0))
        ip = s.getsockname()[0]
        return bytes([int(x) for x in ip.split('.')])
    except socket.gaierror:
        return bytes([0, 0, 0, 0])


if __name__ == '__main__':
    parser = get_args_parser()
    args = parser.parse_args()
    loop = asyncio.get_event_loop()
    listen = loop.create_datagram_endpoint(
        NTPServer, local_addr=('127.0.0.1', args.port))
    transport, protocol = loop.run_until_complete(listen)

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    transport.close()
    loop.close()
