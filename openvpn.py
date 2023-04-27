import subprocess
import requests
import time

# 配置OpenVPN
config_file_path = "./openvpn/config/vpngate_219.100.37.180_tcp_443.ovpn"
openvpn_executable = "openvpn"  # 如果在系统PATH中，请使用 "openvpn"，否则请提供完整路径

# 要测试的URL
test_urls = ["https://www.example.com", "https://www.anotherexample.com"]

def get_outbound_ip():
    ip_check_url = "https://api64.ipify.org"
    try:
        response = requests.get(ip_check_url)
        if response.status_code == 200:
            return response.text
        else:
            print(f"获取出站IP失败，状态码: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"获取出站IP时出现错误: {e}")


def check_url_connectivity(urls):
    for url in urls:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                print(f"成功访问: {url}")
            else:
                print(f"访问失败: {url}，状态码: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"访问URL时出现错误: {e}")

def main():
    # 启动OpenVPN客户端
    openvpn_process = subprocess.Popen([openvpn_executable, "--config", config_file_path])

    # 等待VPN连接建立
    time.sleep(15)  # 请根据实际情况调整等待时间

    # 获取VPN连接后的出站IP
    vpn_outbound_ip = get_outbound_ip()
    print(f"VPN连接后的出站IP: {vpn_outbound_ip}")

    # 测试连接和访问URL
    check_url_connectivity(test_urls)

    # 断开VPN连接
    openvpn_process.terminate()

if __name__ == "__main__":
    main()
