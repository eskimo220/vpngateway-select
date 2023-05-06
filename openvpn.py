import subprocess
import requests
import time
import socket

from openvpn_api import VPN
from urllib.parse import urlparse


# 配置OpenVPN
config_file_path = "./20230505045704/public-vpn-184.ovpn"
openvpn_executable = "openvpn"  # 如果在系统PATH中，请使用 "openvpn"，否则请提供完整路径

# 要测试的URL
test_urls = ["https://www.google.com"]

# OpenVPN管理接口配置
management_ip = "127.0.0.1"
management_port = 7505

# 创建并存储进程对象
processes = []

def dns(domain_name = "ifconfig.me"):
    ip_address = socket.gethostbyname(domain_name)
    print(f"The IP address of {domain_name} is {ip_address}")


def check_url_connectivity(urls=["https://www.google.com"]):
    for url in urls:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                print(f"成功访问: {url}")
            else:
                print(f"访问失败: {url}，状态码: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"访问URL时出现错误: {e}")
            return False
    return True


def get_outbound_ip(ip_check_url = "https://api64.ipify.org"):
    try:
        dns(urlparse(ip_check_url).hostname)
        response = requests.get(ip_check_url,timeout=5)
        if response.status_code == 200:
            return response.text
        else:
            print(f"获取出站IP失败，状态码: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"获取出站IP时出现错误: {e}")


def wait_for_vpn_connection(management_ip, management_port, timeout=60):
    start_time = time.time()

    while time.time() - start_time < timeout:
        try:
            with socket.create_connection(
                (management_ip, management_port), timeout=2
            ) as sock:
                sock.sendall(b"state\n")
                response = sock.recv(4096).decode("utf-8")
                print(response)

            if "CONNECTED,SUCCESS" in response:
                print("VPN连接已建立")
                return True
        except (socket.timeout, ConnectionRefusedError):
            pass

        time.sleep(1)

    print("等待VPN连接超时")
    return False


def wait_for_vpn_connection2(management_ip, management_port, timeout=20):
    start_time = time.time()

    v = VPN(management_ip, management_port)

    while time.time() - start_time < timeout:
        try:
            with v.connection():
                # Do some stuff, e.g.
                print(v.state.state_name)
                v.clear_cache()

                if "CONNECTED" == v.state.state_name:
                    print("VPN连接已建立")
                    return True
        except:
            pass

        time.sleep(1)

    print("等待VPN连接超时")
    return False

def stop_all_process():
    for process in processes.copy():
        process.terminate()
        process.wait()  # 等待进程终止
        processes.remove(process) 


def connect_and_check(config_file_path):
    # 获取原始出站IP
    original_outbound_ip = get_outbound_ip()
    print(f"原始出站IP: {original_outbound_ip}")

    # 启动OpenVPN客户端
    openvpn_process = subprocess.Popen(
        [
            openvpn_executable,
            "--config",
            config_file_path,
            "--management",
            management_ip,
            str(management_port),
        ]
    )

    processes.append(openvpn_process)

    # 等待VPN连接建立
    if not wait_for_vpn_connection(management_ip, management_port):
        print("无法建立VPN连接，终止程序")
        stop_all_process()
        return False

    # 获取VPN连接后的出站IP
    vpn_outbound_ip = get_outbound_ip()
    print(f"VPN连接后的出站IP: {vpn_outbound_ip}")

    if vpn_outbound_ip == original_outbound_ip:
        stop_all_process()
        return False
    # 测试连接和访问URL
    if not check_url_connectivity():
        stop_all_process()
        return False

    return True
    # 断开VPN连接
    # openvpn_process.terminate()


def main():
    # 获取原始出站IP
    original_outbound_ip = get_outbound_ip()
    print(f"原始出站IP: {original_outbound_ip}")

    # 启动OpenVPN客户端
    openvpn_process = subprocess.Popen(
        [
            openvpn_executable,
            "--config",
            config_file_path,
            "--management",
            management_ip,
            str(management_port),
        ]
    )

    # 等待VPN连接建立
    if not wait_for_vpn_connection2(management_ip, management_port):
        print("无法建立VPN连接，终止程序")
        openvpn_process.terminate()
        return

    time.sleep(10)
    # 获取VPN连接后的出站IP
    vpn_outbound_ip = get_outbound_ip()
    print(f"VPN连接后的出站IP: {vpn_outbound_ip}")

    # 测试连接和访问URL
    check_url_connectivity(test_urls)


    time.sleep(120)
    # 断开VPN连接
    openvpn_process.terminate()


if __name__ == "__main__":
    main()
