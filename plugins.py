import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import os
import uuid
import dns.resolver
import socket
import requests
import concurrent.futures


# =========================
# COMMON PORTS (SAFE LIST)
# =========================

COMMON_PORTS = {
    21: "FTP",
    22: "SSH",
    23: "Telnet",
    25: "SMTP",
    53: "DNS",
    80: "HTTP",
    110: "POP3",
    143: "IMAP",
    443: "HTTPS",
    3306: "MySQL",
    3389: "RDP",
    8080: "HTTP-Alt"
}


# =========================
# GRAPH GENERATOR
# =========================

def generate_graph(data_points, graph_type="line"):

    x = list(range(len(data_points)))
    y = data_points

    os.makedirs("static/graphs", exist_ok=True)

    filename = f"graphs/{uuid.uuid4().hex}.png"
    full_path = os.path.join("static", filename)

    plt.figure()

    if graph_type == "bar":
        plt.bar(x, y)

    elif graph_type == "scatter":
        plt.scatter(x, y)

    elif graph_type == "hist":
        plt.hist(y, bins=5)

    elif graph_type == "pie":
        plt.pie(y, labels=[f"P{i}" for i in range(len(y))], autopct="%1.1f%%")

    else:
        plt.plot(x, y)

    plt.title("Generated Graph")
    plt.xlabel("Index")
    plt.ylabel("Value")
    plt.grid(True)

    plt.savefig(full_path)
    plt.close()

    return f"/static/{filename}"

# =========================
# DNS LOOKUP
# =========================

def dns_lookup(domain):
    try:
        result = f"🌐 DNS Summary: {domain}\n\n"

        try:
            answers = dns.resolver.resolve(domain, "A")
            ips = [str(r) for r in answers]
            result += "A Record (IP):\n"
            result += "\n".join(ips) + "\n\n"
        except:
            result += "A Record: Not found\n\n"

        try:
            answers = dns.resolver.resolve(domain, "MX")
            mx = [str(r.exchange) for r in answers]
            result += "MX Record (Mail Server):\n"
            result += "\n".join(mx) + "\n\n"
        except:
            result += "MX Record: Not found\n\n"

        try:
            answers = dns.resolver.resolve(domain, "NS")
            ns = [str(r) for r in answers]
            result += "NS Records (Name Servers):\n"
            result += "\n".join(ns) + "\n"
        except:
            result += "NS Records: Not found\n"

        return result

    except Exception as e:
        return f"DNS lookup failed: {str(e)}"

# =========================
# IP LOOKUP
# =========================

def ip_lookup(ip):
    try:
        response = requests.get(f"http://ip-api.com/json/{ip}", timeout=10)
        data = response.json()

        if data.get("status") != "success":
            return "IP lookup failed."

        return f"""
🌍 IP Lookup for {ip}

Country: {data.get('country')}
Region: {data.get('regionName')}
City: {data.get('city')}
ISP: {data.get('isp')}
Organization: {data.get('org')}
Timezone: {data.get('timezone')}
""".strip()

    except Exception as e:
        return f"IP lookup failed: {str(e)}"


# =========================
# SAFE PORT SCANNER
# =========================

def is_private_ip(ip):
    return (
        ip.startswith("127.") or
        ip.startswith("10.") or
        ip.startswith("192.168.") or
        ip.startswith("172.16.") or
        ip.startswith("172.17.") or
        ip.startswith("172.18.") or
        ip.startswith("172.19.") or
        ip.startswith("172.2")  # covers 172.20–172.29
    )


def scan_port(host, port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            result = s.connect_ex((host, port))
            if result == 0:
                return port
    except:
        pass
    return None


def port_scan(host):
    open_ports = []

    try:
        ip = socket.gethostbyname(host)
    except:
        return f"Could not resolve host: {host}"

    # 🔒 SAFETY RESTRICTION
    if not is_private_ip(ip):
        return (
            f"🚫 Port scanning is restricted on this system.\n\n"
            f"Resolved IP: {ip}\n"
            f"Only localhost or private network ranges are allowed."
        )

    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(scan_port, ip, port) for port in COMMON_PORTS]

        for future in concurrent.futures.as_completed(futures):
            port = future.result()
            if port:
                open_ports.append(port)

    if not open_ports:
        return f"🔍 Port Scan for {host} ({ip})\n\nNo common ports open."

    result = f"🔍 Port Scan for {host} ({ip})\n\nOpen Ports:\n"

    for port in sorted(open_ports):
        service = COMMON_PORTS.get(port, "Unknown")
        result += f"{port} ({service})\n"

    return result