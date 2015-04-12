#!/usr/bin/python3

import argparse
import os
from time import time
from random import randint
import socket
from struct import pack, unpack
from decimal import Decimal
import asyncio
import logging


NTP_PORT = 123
USER_OFFSET = 0
DEFAULT_BUFFER_SIZE = 64 * 1024

NTP_CURRENT_VERSION = 4

NTP_HEADER_FORMAT = ">BBBBII4sQQQQ"
NTP_HEADER_LENGTH = 48
NTP_UTC_OFFSET = 2208988800


def utc_to_ntp_bytes(time):
    return int((Decimal(time) + NTP_UTC_OFFSET) * (2 ** 32))


class Packet(object):
    def __init__(self, leap=0, version=NTP_CURRENT_VERSION,
                 mode=4, stratum=16, poll=0, precision=0, root_delay=0,
                 root_dispersion=0, ref_id=b'\x00' * 4, ref_time=0, origin=0,
                 receive=0, transmit=0):
        self.leap = leap
        self.version = version
        self.mode = mode
        self.options = (self.leap << 6) | (self.version << 3) | self.mode
        self.stratum = stratum
        self.poll_binary = poll
        self.poll = 2 ** (-poll)
        self.precision_binary = precision
        self.root_delay_binary = root_delay
        self.root_dispersion_binary = root_dispersion
        self.ref_id_binary = ref_id
        self.ref_time_binary = ref_time
        self.origin_binary = origin
        self.receive_binary = receive
        self.transmit_binary = transmit

    @classmethod
    def from_binary(cls, data):
        (options, stratum, poll, precision, root_delay, root_dispersion,
            ref_id, ref_time, origin, receive, transmit) = unpack(
            NTP_HEADER_FORMAT, data[:NTP_HEADER_LENGTH])
        leap, version, mode = options >> 6, (
            (options >> 3) & 0x7), options & 0x7
        return Packet(leap, version, mode, stratum, poll, precision,
                      root_delay, root_dispersion, ref_id, ref_time, origin,
                      receive, transmit)

    def to_binary(self):
        return pack(NTP_HEADER_FORMAT,
                    self.options,
                    self.stratum,
                    self.poll_binary,
                    self.precision_binary,
                    self.root_delay_binary,
                    self.root_dispersion_binary,
                    self.ref_id_binary,
                    self.ref_time_binary,
                    self.origin_binary,
                    self.receive_binary,
                    self.transmit_binary)


class SNTPServer(asyncio.Protocol):
    """docstring for SNTPServer"""
    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        packet = Packet.from_binary(data)
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
    parser = argparse.ArgumentParser(description="NTP tool")
    parser.add_argument("--delay",
                        help="Set delay",
                        type=int,
                        default=0)
    parser.add_argument("-p", "--port",
                        help="port", type=int, default=5000)
    return parser


def get_my_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('google.com', 0))
    ip = s.getsockname()[0]
    return bytes([int(x) for x in ip.split('.')])


if __name__ == '__main__':
    parser = get_args_parser()
    args = parser.parse_args()
    loop = asyncio.get_event_loop()
    logging.basicConfig(level=logging.INFO)
    listen = loop.create_datagram_endpoint(
        SNTPServer, local_addr=('127.0.0.1', args.port))
    transport, protocol = loop.run_until_complete(listen)

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    transport.close()
    loop.close()
