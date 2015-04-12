#!/usr/bin/python3

import argparse
from select import select
from time import time, strftime, gmtime
from socket import socket, AF_INET, SOCK_DGRAM
from common import *
from hexdump import *


def get_args():
    parser = argparse.ArgumentParser(
        description="NTP tool")
    parser.add_argument(
        "source",
        help="Source server address")
    parser.add_argument(
        "-v", "--version",
        help="NTP version to be used",
        default=NTP_CURRENT_VERSION,
        type=int)
    parser.add_argument(
        "-t", "--timeout",
        help="Timeout in seconds (default 1)",
        default=1,
        type=int)
    parser.add_argument(
        "-a", "--attempts",
        help="Maximum attempts (default 5)",
        default=5,
        type=int)
    parser.add_argument(
        "-f", "--file",
        help="Use source as filename of NTP packet dump",
        action='store_true')
    parser.add_argument(
        "-u", "--show-utc",
        help="Show UTC interpretation of time",
        action='store_true')
    args = parser.parse_args()
    return args


def get_address(source):
    """Return address and port"""
    chunks = source.split(':')
    return chunks[0], int(chunks[1]) if len(chunks) > 1 else NTP_PORT


def get_raw_packet(args):
    """Get packet"""
    if args.file:
        try:
            with open(args.source, "rb") as file:
                return file.read()
        except OSError as e:
            exit(e)
    request = request_packet(version=args.version).to_binary()
    for attempt in range(1, args.attempts + 1):
        try:
            address = get_address(args.source)
            with socket(AF_INET, SOCK_DGRAM) as sock:
                sock.sendto(request, address)
                if select([sock], [], [], args.timeout)[0]:
                    return sock.recvfrom(1024)[0]
        except Exception as e:
            pass
        print("Attempt {} failed".format(attempt))
    return bytes(0)


def get_clock_offset(packet):
    """Return clock offset"""
    current_ntp_time = time() + NTP_UTC_OFFSET
    trip_delay = (packet.receive - packet.origin) / 2
    return Decimal(current_ntp_time) - packet.transmit - trip_delay


if __name__ == "__main__":
    args = get_args()
    raw_packet = get_raw_packet(args)
    if raw_packet:
        packet = packet_from_binary(raw_packet)
        print(get_packet_hexdump(packet, args.show_utc))
        clock_offset = get_clock_offset(packet)
        print('Local clock offset: {} sec'.format(
            clock_offset))
    else:
        print("Failed")
