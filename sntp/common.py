from time import time, strftime, gmtime
from decimal import Decimal
from ipaddress import IPv4Address
from struct import pack, unpack

NTP_PORT = 123

NTP_CURRENT_VERSION = 4

NTP_HEADER_FORMAT = ">BBBBII4sQQQQ"
NTP_HEADER_LENGTH = 48
NTP_UTC_OFFSET = 2208988800


def utc_to_ntp_bytes(time):
    return int((Decimal(time) + NTP_UTC_OFFSET) * (2 ** 32))


def utc_to_string(value):
    return strftime("%a, %d %b %Y %H:%M:%S UTC", gmtime(value))


def from_ntp_short_bytes(value):
    return Decimal(value) / (2 ** 16)


def from_ntp_time_bytes(value):
    return Decimal(value) / (2 ** 32)


class Packet(object):
    def __init__(self,
                 leap=0,
                 version=NTP_CURRENT_VERSION,
                 mode=3, stratum=16, poll=0,
                 precision=0, root_delay=0,
                 root_dispersion=0, ref_id=b'\x00' * 4,
                 ref_time=0, origin=0, receive=0,
                 transmit=0):
        self.leap = leap
        self.version = version
        self.mode = mode
        self.options = (self.leap << 6) | (self.version << 3) | self.mode
        self.stratum = stratum
        self.poll_binary = poll
        self.poll = 2 ** (-poll)
        self.precision_binary = precision
        self.precision = 2 ** (-precision)
        self.root_delay_binary = root_delay
        self.root_delay = from_ntp_short_bytes(root_delay)
        self.root_dispersion_binary = root_dispersion
        self.root_dispersion = from_ntp_short_bytes(root_dispersion)
        self.ref_id_binary = ref_id
        self.ref_id = str(IPv4Address(ref_id))
        self.ref_time_binary = ref_time
        self.ref_time = from_ntp_time_bytes(ref_time)
        self.origin_binary = origin
        self.origin = from_ntp_time_bytes(origin)
        self.receive_binary = receive
        self.receive = from_ntp_time_bytes(receive)
        self.transmit_binary = transmit
        self.transmit = from_ntp_time_bytes(transmit)

    def to_binary(self):
        return pack(
            NTP_HEADER_FORMAT,
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


def request_packet(version=NTP_CURRENT_VERSION):
    current_time = time()
    return Packet(version=version, transmit=utc_to_ntp_bytes(current_time))


def packet_from_binary(data):
    (options, stratum, poll, precision, root_delay,
     root_dispersion, ref_id, ref_time,
     origin, receive, transmit) = unpack(
        NTP_HEADER_FORMAT, data[:NTP_HEADER_LENGTH])
    leap, version, mode = options >> 6, (
        (options >> 3) & 0x7), options & 0x7
    return Packet(leap, version, mode, stratum, poll, precision,
                  root_delay, root_dispersion, ref_id, ref_time,
                  origin, receive, transmit)
