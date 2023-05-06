import signal
import logging
from downloadCsv import dlcsv
from openvpn import connect_and_check, check_url_connectivity, stop_all_process
import time
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

is_test = os.getenv("TEST")

# Set flag to indicate if program is running
running = True

def signal_handler(sig, frame):
    """
    Signal handler function to handle interruption signals
    """
    global running
    logging.info("Program interrupted. Cleaning up...")
    running = False

def main():
    """
    The main function connects to each node and checks the VPN connectivity. If the VPN connectivity is established, the program enters an inner loop 
    that checks the connectivity to a specific URL every minute. If the program detects that the URL connectivity is lost, 
    it will restart the process from the beginning and try again. If the program cannot establish VPN connectivity for any node, it will exit with a failure status.
    """
    global running

    # Download list of nodes
    nodes = dlcsv()

    if bool(is_test):
        nodes = nodes[:3]

    # Flag to indicate if VPN connectivity is established for any node
    vpn_ok = False

    # Connect to each node and check VPN connectivity
    for node in nodes:
        logging.info(f"Connecting to {node['ovpnfile']}")
        if not running:
            stop_all_process()
            break
        if connect_and_check(node["ovpnfile"]):
            logging.info("VPN connectivity established.")
            vpn_ok = True
            break

    # If VPN connectivity is established, wait for URL connectivity
    if vpn_ok:
        if bool(is_test):
            stop_all_process()
            exit(0)

        while running:
            time.sleep(60)
            if not running:
                stop_all_process()
                break
            if not check_url_connectivity():
                logging.info("URL connectivity lost. Retrying.")
                stop_all_process()
                break
    else:
        logging.error("VPN connectivity not established for any node.")
        exit(1)


if __name__ == "__main__":
    # Start the program
    logging.info("Program started.")

    if bool(is_test):
        logging.warn("TEST MODE.")
    
    # Register signal handler for interruption signals
    signal.signal(signal.SIGINT, signal_handler)

    # Run the main loop
    while running:
        main()

    # End the program
    logging.info("Program ended.")
