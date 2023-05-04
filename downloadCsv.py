import base64
import os
import shutil
import datetime
import csv
import requests


def download_csv_file(url, dir_name):
    response = requests.get(url)
    csvfile = os.path.join(dir_name, 'vpn_servers.csv')
    with open(csvfile, 'wb') as f:
        f.write(response.content)
    return csvfile


def filter_and_sort_data(csvfile):
    with open(csvfile, 'r', encoding='utf-8') as f:
        f.readline()
        csv_reader = csv.DictReader(f)
        data = list(csv_reader)
        data = [row for row in data if row['CountryShort'] in ["JP", "US"]]
        sorted_data = sorted(data, key=lambda x: int(x['Score']), reverse=True)
    return sorted_data


def print_and_save_data(sorted_data, dir_name):
    for row in sorted_data:
        truncated_row = [row[cell][:20] if len(row[cell]) > 20 else row[cell] for cell in row]
        print(truncated_row)
        ovpnfile = os.path.join(dir_name, row['#HostName'] + '.ovpn')
        with open(ovpnfile, 'wb') as file:
            file.write(base64.b64decode(row['OpenVPN_ConfigData_Base64']))


def dlcsv():
    dir_name = datetime.datetime.now().strftime('%Y%m%d%H%M%S')

    if os.path.exists(dir_name):
        shutil.rmtree(dir_name)

    os.makedirs(dir_name)

    url = 'http://www.vpngate.net/api/iphone/'
    csvfile = download_csv_file(url, dir_name)
    sorted_data = filter_and_sort_data(csvfile)
    print_and_save_data(sorted_data, dir_name)

    return sorted_data


if __name__ == '__main__':
    dlcsv()
