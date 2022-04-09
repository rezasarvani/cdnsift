import argparse
import sys
import os
import requests
import urllib3
import json
import socket
import ipaddress


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
parser = argparse.ArgumentParser(description="cdnsift: Filter IP Addresses That Are In CDN Ranges")

parser.add_argument("-i", "--input",
                    default="-",
                    help='Enter your IP list file path. (Default: - [pass from stdin])')

parser.add_argument("-v", "--verbose",
                    action="store_true",
                    default=False,
                    help='Return IP ranges with CDN information.')

parser.add_argument("-d", "--debug",
                    action="store_true",
                    default=False,
                    help='Show more debug messages.')

parser.add_argument("-du", "--disable-update",
                    action="store_true",
                    default=False,
                    help='Do not update ranges.txt file.')

parser.add_argument("-o", "--output",
                    default=False,
                    help='Location of output file. (Don\'t use this switch if you wish to print the result to STDOUT)')

parser.add_argument("-r", "--reverse",
                    action="store_true",
                    default=False,
                    help='Return result for IP addresses that are in CDN ranges.')

parser.add_argument("-a", "--append",
                    default=False,
                    help='Append a list of CDN ranges (One range per each line.)')

options = parser.parse_args()

def verbose_print(message):
    if options.debug:
        print(message)

def validate(ipaddress):
    try:
        socket.inet_aton(ipaddress)
        return ipaddress
    except socket.error:
        return False

def save_output(ip_list):
    if not options.output:
        for ip in ip_list:
            print(ip)
    else:
        output_handle = open(options.output, "w", encoding="utf-8", errors="ignore")
        for ip in ip_list:
            output_handle.write(f"{ip}\n")

if options.input != "-" and not os.path.exists(options.input):
    print(f"[-] No File Found. [{options.input}]")
    sys.exit(0)

def fetch_latest_ranges():
    request_url = "https://cdn.nuclei.sh"
    try:
        response = requests.get(request_url, verify=False, allow_redirects=True, timeout=5).json()
    except Exception as e:
        verbose_print(f"[-] Failed To Update ranges.txt\n\t[Err] {e}")
        return -1
    file_handle = open("ranges.txt", "w", encoding="utf-8", errors="ignore")
    json.dump(response, file_handle)
    verbose_print("[*] Fetched Latest ranges.txt")

if not options.disable_update:
    fetch_latest_ranges()
if not os.path.exists("ranges.txt"):
    verbose_print("[*] Fetching Latest CDN Ranges.")
    fetch_latest_ranges()

ip_list = []
if options.input == "-":
    for ip in sys.stdin:
        ip = ip.strip()
        ip_list.append(ip)
else:
    file_handle = open(options.input, "r", encoding="utf-8", errors="ignore")
    for ip in file_handle.readlines():
        ip = ip.strip()
        ip_list.append(ip)

ranges_handle = open("ranges.txt", "r", encoding="utf-8", errors="ignore")
cdn_ranges = json.load(ranges_handle)
cdn_ranges["appended"] = []
ranges_handle.close()

if options.append:
    if not os.path.exists(options.append):
        verbose_print(f"[-] Appended File Does Not Exist. [{options.append}]")
    else:
        append_handle = open(options.append, "r", encoding="utf-8", errors="ignore")
        for range in append_handle.readlines():
            range = range.strip()
            cdn_ranges["appended"].append(range)

clean_ips = []
dirty_ips = []

for ip in ip_list:
    if not validate(ip):
        verbose_print(f"[-] Skipping [{ip}]")
        continue
    is_CDN = False
    for cdn_name in cdn_ranges:
        for cdn_range in cdn_ranges[cdn_name]:
            try:
                if ipaddress.ip_address(ip) in ipaddress.ip_network(cdn_range):
                    is_CDN = True
                    if options.reverse:
                        if not options.verbose:
                            dirty_ips.append(ip)
                        else:
                            dirty_ips.append(f"{ip}-{cdn_name}")
                    break
            except Exception as e:
                verbose_print(f"[-] Failed To Compare [{ip}] To [{cdn_range}]")
                continue

        if is_CDN:
            break
    if not is_CDN:
        if not options.reverse:
            clean_ips.append(ip)

if len(clean_ips) > 0:
    save_output(clean_ips)
else:
    save_output(dirty_ips)
