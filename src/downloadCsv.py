import base64
import os
import shutil
import datetime
import csv
import requests
import logging
from urllib3.util import Retry
from requests.adapters import HTTPAdapter

# Set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

session = requests.Session()
   
retries = Retry(total=5,
                backoff_factor=1,
                status_forcelist=[429, 500, 503])

session.mount("https://", HTTPAdapter(max_retries=retries))

def download_csv_file(url, dir_name):
    """Downloads a CSV file from the provided URL and saves it in the specified directory."""
    response = session.get(url, timeout=10)
    csvfile = os.path.join(dir_name, "vpn_servers.csv")
    with open(csvfile, "wb") as f:
        f.write(response.content)
    return csvfile


def filter_and_sort_data(csvfile):
    """Filters the data based on specific country codes and sorts the data based on scores."""
    with open(csvfile, "r", encoding="utf-8") as f:
        f.readline()
        csv_reader = csv.DictReader(f)
        data = list(csv_reader)
        data = [row for row in data if row["CountryShort"] in ["JP"] and not row["IP"].startswith("219.100.37") ]
        sorted_data = sorted(data, key=lambda x: int(x["Score"]), reverse=True)
    return sorted_data


def print_and_save_data(sorted_data, dir_name):
    """Prints the sorted data and saves it as individual .ovpn files."""
    for idx, row in enumerate(sorted_data):
        truncated_row = [
            row[cell][:20] if len(row[cell]) > 20 else row[cell] for cell in row
        ]
        print(truncated_row)
        ovpnfile = os.path.join(dir_name, '{:>03d}'.format(idx) + "---" + row["IP"] + ".ovpn")
        row["ovpnfile"] = ovpnfile
        with open(ovpnfile, "wb") as file:
            file.write(base64.b64decode(row["OpenVPN_ConfigData_Base64"]))


def dlcsv():
    """Main function to download, filter, sort and save the data."""
    dir_name = datetime.datetime.now().strftime("%Y%m%d")

    if os.path.exists(dir_name):
        shutil.rmtree(dir_name)
        logging.info(f"Removed existing directory: {dir_name}")

    os.makedirs(dir_name)
    logging.info(f"Created new directory: {dir_name}")

    url = "http://www.vpngate.net/api/iphone/"
    csvfile = download_csv_file(url, dir_name)
    logging.info(f"Downloaded CSV file: {csvfile}")

    sorted_data = filter_and_sort_data(csvfile)
    logging.info("Filtered and sorted data")

    print_and_save_data(sorted_data, dir_name)
    logging.info("Printed and saved data as .ovpn files")

    return sorted_data


if __name__ == "__main__":
    dlcsv()
