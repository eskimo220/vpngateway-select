from downloadCsv import dlcsv
from openvpn2 import connect_and_check, check_url_connectivity, stop_all_process
import time


def main():

    while True:
        nodes = dlcsv()

        isOk = False
        for node in nodes:
            if connect_and_check(node["ovpnfile"]):
                print("vpn is ok. wait 1 min to check again")
                isOk = True
                break

        if isOk:
            while True:
                time.sleep(60)
                if not check_url_connectivity():
                    print("vpn is no longer ok. retry")
                    stop_all_process()
                    break
        else:
            print("something went wrong.")
            return False


if __name__ == "__main__":
    main()
