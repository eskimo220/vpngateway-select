import subprocess
import requests
import time
import socket
import logging
import os
from openvpn_api import VPN
from urllib.parse import urlparse

# Configuration
config_file_path = "./20230505045704/public-vpn-184.ovpn"
openvpn_executable = "openvpn"
test_urls = ["https://www.google.com"]
management_ip = "127.0.0.1"
management_port = 7505
processes = []

# Set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def dns(domain_name="ifconfig.me"):
    """Retrieve the IP address of a given domain."""
    try:
        ip_address = socket.gethostbyname(domain_name)
        logging.info(f"The IP address of {domain_name} is {ip_address}")
    except:
        logging.error(f"can not resolve {domain_name}")
        pass

def check_url_connectivity(urls=["https://www.google.com"]):
    """Check the connectivity to a list of URLs."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    for url in urls:
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                logging.info(f"Successfully accessed: {url}")
            else:
                logging.error(f"Failed to access: {url}, status code: {response.status_code}, response text: {response.text[:500]}")
                return False
        except requests.exceptions.RequestException as e:
            logging.error(f"Error occurred while accessing URL: {e}")
            return False
    return True

def get_outbound_ip(ip_check_url="https://ifconfig.me"):
    """Retrieve the outbound IP address."""
    try:
        dns(urlparse(ip_check_url).hostname)
        response = requests.get(ip_check_url, timeout=5)
        if response.status_code == 200:
            return response.text
        else:
            logging.error(f"Failed to get outbound IP, status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error occurred while getting outbound IP: {e}")

def wait_for_vpn_connection(management_ip, management_port, timeout=3000):
    """Wait for the VPN connection to be established."""
    start_time = time.time()

    while time.time() - start_time < timeout:
        try:
            with socket.create_connection(
                (management_ip, management_port), timeout=2
            ) as sock:
                sock.sendall(b"state\n")
                
                response = ""
                # Continue reading from the socket until 'END' is found
                while "END" not in response:
                    part = sock.recv(4096).decode("utf-8")
                    if not part:  # If no more data is received, break the loop
                        break
                    response += part

                # Log the received response
                logging.info(response)

            if "CONNECTED,SUCCESS" in response:
                logging.info("VPN connection established")
                return True
        except (socket.timeout, ConnectionRefusedError):
            pass

        time.sleep(1)

    logging.error("Waiting for VPN connection timed out")
    return False

def wait_for_vpn_connection2(management_ip, management_port, timeout=30):
    """Wait for the VPN connection to be established (alternative method)."""
    start_time = time.time()

    v = VPN(management_ip, management_port)

    while time.time() - start_time < timeout:
        try:
            with v.connection():
                logging.info(v.state.state_name)
                v.clear_cache()

                if "CONNECTED" == v.state.state_name:
                    logging.info("VPN connection established")
                    return True
        except:
            pass

        time.sleep(1)

    logging.error("Waiting for VPN connection timed out")
    return False

def stop_all_process():
    """Terminate all running processes."""
    for process in processes.copy():
        process.terminate()
        process.wait()
        processes.remove(process)

def connect_and_check(config_file_path):
    """Connect to the VPN and check if the connection is successful."""
    original_outbound_ip = get_outbound_ip()
    logging.info(f"Original outbound IP: {original_outbound_ip}")

    options = [
        openvpn_executable,
        "--config",
        config_file_path,
        "--management",
        management_ip,
        str(management_port),
        "--script-security",
        "2",
        "--data-ciphers",
        "AES-128-CBC:AES-256-GCM:AES-128-GCM:CHACHA20-POLY1305"
    ]

    if os.path.exists("/etc/openvpn/update-resolv-conf"):
        options.extend([
            "--up",
        "/etc/openvpn/update-resolv-conf",
        "--down",
        "/etc/openvpn/update-resolv-conf"
        ])
    elif os.path.exists("/etc/openvpn/up.sh"):
        options.extend([
            "--up",
        "/etc/openvpn/up.sh",
        "--down",
        "/etc/openvpn/down.sh"
        ])
    else:
        logging.error("can not find dns shell.")
        exit(1)

    openvpn_process = subprocess.Popen(options)

    processes.append(openvpn_process)

    if not wait_for_vpn_connection(management_ip, management_port):
        logging.error("Cannot establish VPN connection, terminating program")
        stop_all_process()
        return False

    vpn_outbound_ip = get_outbound_ip()
    logging.info(f"Outbound IP after VPN connection: {vpn_outbound_ip}")

    if vpn_outbound_ip == original_outbound_ip:
        stop_all_process()
        return False

    if not check_url_connectivity():
        stop_all_process()
        return False

    return True
