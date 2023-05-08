# VPN Autoconnect Tool

## 1. Introduction

The VPN Autoconnect Tool is designed to automatically connect to a VPN to solve the problem of being unable to use popular tools like ChatGPT due to IP issues. This tool can automatically obtain VPN node information from [VPN Gate 学術実験サービス](https://www.vpngate.net/ja/), connect to a VPN using OpenVPN, and check the connection every minute to ensure the VPN connection is available. This tool can be run in a Docker container to avoid modifying the local network.

## 2. Installation and Running

### 2.1 Installation

- Download or clone this project.
- In the root directory of the project, run `docker build -t vpngateway-select:alpine -f Dockerfile.alpine .` to build the Docker image.

### 2.2 Running

- In the root directory of the project, run the following command to start the Docker container:

```
docker run --cap-add=NET_ADMIN --device=/dev/net/tun --name vpn-autoconnect vpn-autoconnect
```

### 2.3 Share the network with other docker containers

docker-compose.yml
```
version: "3"
services:
  openvpn-client:
    image: eskimo220/vpngateway-select
    container_name: openvpn-client
    cap_add:
      - NET_ADMIN
    devices:
      - /dev/net/tun
    ports:
      - "8080:8080"
      - "35408:35408"
      
  xui:
    image: enwaiax/x-ui
    network_mode: service:openvpn-client
    volumes:
      - ./db:/etc/x-ui/
```


## 3. Notes

The intended operating environment for this tool is a free network environment, which means it should be deployed and run on a self-built ladder node. If you run this tool directly in China, it will most likely be unable to connect to the VPN server. In this case, it is recommended to use TUN proxy in software like Clash to form a chained proxy.
This tool checks the connection every minute and will automatically retry if the connection fails. Please note that if the VPN connection is interrupted, this tool will attempt to reconnect, which may cause a brief interruption in your network connection.

## 4. Contributions

If you find any bugs or have suggestions for improvements, please feel free to submit an Issue or Pull Request.

## 5. License

This tool is licensed under the MIT License. Please see the LICENSE file for details.