#!/usr/bin/python
import socket
import csv
import argparse
from sys import argv
db = {}


def get_args():
    parser = argparse.ArgumentParser(description="NTP tool")
    parser.add_argument("goals",
                        help="one or more IPv4 address",
                        nargs="+")
    parser.add_argument("-l", "--max-hops",
                        help="maximum hops limit",
                        default=30, type=int)
    parser.add_argument("-t", "--timeout",
                        help="set timeout",
                        default=5, type=int)
    args = parser.parse_args()
    return args


def whois(ip, server):
    whois_data = {
        "country": "",
        "AS": "",
        "netname": ''
    }

    if not server:
        return whois_data

    if server == 'whois.arin.net':
        _country = "Country:"
        _as = "OriginAS:"
        _netname = "NetName:"
    else:
        _country = "country:"
        _as = "origin:"
        _netname = "netname:"

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((server, 43))

    try:
        sock.send(ip.encode("cp866")+b'\n')
        data = sock.recv(10000).decode("cp866")
        while data:
            _data = data
            data = " ".join(data.split())
            try:
                country_index = data.index(_country) + len(_country) + 1
                whois_data['country'] = data[country_index:country_index+2]
                as_index = data.index(_as) + len(_as) + 1
                _AS = data[as_index:as_index+12].split(" ")[0]
                if (whois_data['AS'][:2] != "AS") and (_AS != "Organizat"):
                    whois_data['AS'] = _AS
            except ValueError as e:
                try:
                    as_index = data.index(_as) + len(_as) + 1
                    _AS = data[as_index:as_index+12].split(" ")[0]
                    try:
                        if whois_data['AS'][:2] != "AS":
                            whois_data['AS'] = _AS
                    except:
                        pass
                except ValueError as e:
                    pass
            data = sock.recv(10000).decode("cp866")
    except socket.error:
        pass
    finally:
        sock.close()
    return whois_data


def tracert(dest_name, max_hops=30, timeout=5):
    goal = dest_name
    try:
        dest_addr = socket.gethostbyname(dest_name)
    except socket.gaierror:
        exit("Serious!? Check the address, now!")
    print("Start traceroute to {} ({})".format(dest_name, dest_addr))
    print("#\tIP\t\tCountry\tAS\tHost Name")
    port = 33434
    icmp = socket.getprotobyname('icmp')
    udp = socket.getprotobyname('udp')
    ttl = 1
    while True:
        recv_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
        send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, udp)
        send_socket.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)
        recv_socket.settimeout(timeout)
        recv_socket.bind((b"", port))
        send_socket.sendto(b"", (dest_name, port))
        curr_addr = None
        curr_name = None
        try:
            _, curr_addr = recv_socket.recvfrom(512)
            curr_addr = curr_addr[0]
            try:
                curr_name = socket.gethostbyaddr(curr_addr)[0]
            except socket.error:
                curr_name = curr_addr
        except socket.error as e:
            pass
        finally:
            send_socket.close()
            recv_socket.close()

        if curr_addr is not None:
            prefix = int(curr_addr.split('.')[0])
            server = db[prefix]
            whs = whois(curr_addr, server)
            curr_host = "{}\t{}\t{}\t{}".format(curr_addr,
                        whs['country'], whs['AS'], curr_name)
        else:
            curr_host = "*"
        print("{}\t{}".format(ttl, curr_host))

        ttl += 1
        if curr_addr == dest_addr:
            print("{} is reached, for {} hops".format(goal, ttl-1))
            break
        elif ttl > max_hops:
            print("{} is don't reached".format(goal, ttl-1))
            break

if __name__ == "__main__":
    args = get_args()
    with open('ipv4-address-space.csv') as csv_file:
        data = csv.reader(csv_file)
        for rec in data:
            if rec[0] != 'Prefix':
                db[int(rec[0][:3])] = rec[3]
            else:
                pass
    for goal in args.goals:
        tracert(goal, args.max_hops, args.timeout)
