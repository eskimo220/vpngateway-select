from downloadCsv import dlcsv
from openvpn2 import connect_and_check, check_url_connectivity
import time


def main():
    nodes = dlcsv()

    isOk = False
    for node in nodes:
        if connect_and_check(node["ovpnfile"]):
            isOk = True
            break

    if isOk:
        while True:
            time.sleep(60)
            if not check_url_connectivity():
                break
    else:
        return False


if __name__ == "__main__":
    main()
