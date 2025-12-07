import nmap
import socket
import ipaddress
import sys


def get_local_ip():
    """
    Tricks the OS into revealing the IP address used to connect to the internet.
    We don't actually send data to Google (8.8.8.8), we just open a socket.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # We don't actually have to connect, just try to route to an external IP
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
    except Exception:
        local_ip = "127.0.0.1"
    finally:
        s.close()
    return local_ip


def get_network_range(ip):
    """
    Takes a local IP (e.g. 192.168.1.50) and assumes a standard home /24 subnet.
    Returns: 192.168.1.0/24
    """
    # Create an interface object (IP + Subnet Mask)
    # We assume /24 because 99% of home routers use this.
    try:
        network = ipaddress.IPv4Interface(f"{ip}/24").network
        return str(network)
    except ValueError:
        return None


def scan_home_network(network_range):
    nm = nmap.PortScanner()
    print(f"🔎 Scanning your network ({network_range})... please wait.")

    try:
        # -sn: Ping Scan (disable port scan) - fast discovery
        # sudo is usually required to get MAC addresses
        nm.scan(hosts=network_range, arguments="-sn")
    except nmap.PortScannerError:
        print("Error: Nmap not found or permission denied.")
        sys.exit()

    found_devices = []

    for host in nm.all_hosts():
        # Try to get MAC address (Requires sudo/admin rights!)
        if "mac" in nm[host]["addresses"]:
            mac = nm[host]["addresses"]["mac"]
            vendor = nm[host]["vendor"].get(mac, "Unknown Vendor")
        else:
            mac = "Unknown (Run as Admin/Root to see)"
            vendor = "Unknown"

        hostname = nm[host].get("hostnames", [{"name": ""}])[0]["name"]
        if not hostname:
            hostname = "No Hostname"

        found_devices.append(
            {"ip": host, "mac": mac, "vendor": vendor, "hostname": hostname}
        )

    return found_devices


def main():
    print("--- 🏠 Home Network Monitor ---")

    # 1. Auto-Detect Network
    my_ip = get_local_ip()
    print(f"Your IP is: {my_ip}")

    target_range = get_network_range(my_ip)
    if not target_range:
        print("Could not detect network range.")
        target_range = input("Please enter manually (e.g. 192.168.1.0/24): ")

    print(f"Targeting Network: {target_range}\n")

    # 2. Perform Scan
    devices = scan_home_network(target_range)

    # 3. Interactive Results
    print(
        f"✅ Scan Complete. Found {len(devices)} devices connected to your Wi-Fi/LAN.\n"
    )

    for i, d in enumerate(devices, 1):
        print(f"[{i}] IP: {d['ip']}")
        print(f"    Vendor: {d['vendor']}")
        print(f"    Name:   {d['hostname']}")
        print(f"    MAC:    {d['mac']}")
        print("-" * 30)

    # 4. (Optional) Save to DB would go here
    # This is where you would iterate through 'devices' and ask the user to label them
    # like in the previous example.


if __name__ == "__main__":
    main()
