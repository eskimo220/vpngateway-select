import csv
import requests

# 下载csv文件
url = 'http://www.vpngate.net/api/iphone/'
response = requests.get(url)

# 将csv文件写入磁盘
with open('vpn_servers.csv', 'wb') as f:
    f.write(response.content)

# 读取csv文件并处理数据
with open('vpn_servers.csv', 'r') as f:
    f.readline()
    csv_reader = csv.DictReader(f)
    for row in csv_reader:
        hostname = row['#HostName']
        ip = row['IP']
        score = row['Score']
        ping = row['Ping']
        speed = row['Speed']
        country_long = row['CountryLong']
        country_short = row['CountryShort']
        num_vpn_sessions = row['NumVpnSessions']
        uptime = row['Uptime']
        total_users = row['TotalUsers']
        total_traffic = row['TotalTraffic']
        log_type = row['LogType']
        operator = row['Operator']
        message = row['Message']
        # openvpn_config_data = row['OpenVPN_ConfigData_Base64']
        
        # 在这里对数据进行处理
        print(hostname, ip, score, ping, speed, country_long, country_short, num_vpn_sessions, uptime, total_users, total_traffic, log_type, operator, message)
