from struct import pack, unpack
from common import *
LEAP_STRING = [
    "No warning",
    "Last minute of the day has 61 seconds",
    "Last minute of the day has 59 seconds",
    "Unknown (clock unsynchronized)"]

MODE_STRING = [
    "Reserved",
    "Symmetric active",
    "Symmetric passive",
    "Client",
    "Server",
    "Broadcast",
    "NTP control message",
    "Reserved for private use"]


def get_bytes(value, size=None):
    """Return bytes string for hexdump"""
    if isinstance(value, bytes):
        return " ".join(["{:02X}".format(e) for e in value])
    if isinstance(value, int):
        if size == 1:
            return get_bytes(pack('>B', value))
        if size == 4:
            return get_bytes(pack('>I', value))
        if size == 8:
            return get_bytes(pack('>Q', value))


def get_bits(size, bits_count, bits_offset, value):
    """Return bits string for hexdump"""
    _bytes = pack('>I', value)
    binary_string = ''.join(['{0:08b}'.format(byte) for byte in _bytes])
    bits = '.' * bits_offset + binary_string[-bits_count:] + '.' * (
        size * 8 - bits_count - bits_offset)
    return bits


def hexdump(series):
    """Generate pretty hexdump"""
    offset = 0
    result = ''
    for row in series:
        if len(row) == 4:
            # work with `bytes` string
            size, title, binary_value, value = row
            result += "{:0>4X}: {:30}{}: {}\n".format(
                offset, get_bytes(binary_value, size), title, str(value))
            offset += size
        else:
            # work with `bits` string
            size, pieces = row
            _result = ''
            bits_offset = 0
            for piece in pieces:
                bits_count, title, binary_value, value = piece
                _result += '      {:29} {}: {}\n'.format(
                    get_bits(size, bits_count, bits_offset, binary_value),
                    title,
                    str(value))
                bits_offset += bits_count
            result += ('{:0>4X}:'.format(offset)) + _result[5:]
            offset += size
    return result


def get_time_string(time, show_utc):
    """Return time string, optional convert to UTC"""
    return str(time) + (' [{}]'.format(utc_to_string(
        max(time - NTP_UTC_OFFSET, 0)) if show_utc else ''))


def get_packet_hexdump(packet, show_utc):
    """Wrapper for packet dumping"""
    return hexdump((
        (1,
         ((2, 'Leap', packet.leap, LEAP_STRING[packet.leap]),
          (3, 'Version', packet.version, packet.version),
          (3, 'Mode', packet.mode, MODE_STRING[packet.mode]))),
        (1, 'Stratum', packet.stratum, packet.stratum),
        (1, 'Poll', packet.poll_binary, packet.poll),
        (1, 'Precision', packet.precision_binary, packet.precision),
        (4, 'Root delay', packet.root_delay_binary, packet.root_delay),
        (4, 'Root dispersion',
         packet.root_dispersion_binary,
         packet.root_dispersion),
        (4, 'Reference ID', packet.ref_id_binary, packet.ref_id),
        (8, 'Reference timestamp',
         packet.ref_time_binary,
         get_time_string(packet.ref_time, show_utc)),
        (8, 'Origin timestamp',
         packet.origin_binary,
         get_time_string(packet.origin, show_utc)),
        (8, 'Receive timestamp',
         packet.receive_binary,
         get_time_string(packet.receive, show_utc)),
        (8, 'Transmit timestamp',
         packet.transmit_binary,
         get_time_string(packet.transmit, show_utc))
    ))
