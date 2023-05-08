# VPN自动连接工具
### [English](README_EN.md)
## 1. 介绍

本工具是一个自动连接VPN的工具，旨在解决使用chatgpt等人气工具时，由于IP问题而被无法使用的情况。该工具可以自动从[VPN Gate 学術実験サービス](https://www.vpngate.net/ja/)获取VPN节点信息，使用openvpn连接VPN，并每分钟检查连接，以确保VPN连接可用性。该工具可以在Docker容器中运行，避免对本机网络进行修改。

## 2. 安装和运行

### 2.1 安装

- 下载或克隆本项目。
- 在项目根目录下，运行`docker build -t vpngateway-select:alpine -f Dockerfile.alpine .`来构建Docker镜像。

### 2.2 运行

- 在项目根目录下，运行以下命令来启动Docker容器：

```
docker run --cap-add=NET_ADMIN --device=/dev/net/tun --name vpn-autoconnect vpn-autoconnect
```

### 2.3 把网络共享给其他docker container

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


## 3. 注意事项

本工具的想定运行环境是自由网络环境，也就是部署运行在自建的梯子节点上。如果您在中国直接运行该工具，大概率会无法连接到VPN服务器。此时，建议使用Clash等软件的TUN代理，从而形成链式代理。
该工具会在每分钟检查连接，如果连接不上或连接失败会自动重试。请注意，如果 VPN 连接被中断，该工具会尝试重新连接，可能会导致您的网络连接出现短暂的中断。

## 贡献

如果您发现了任何 bug 或者有改进的建议，欢迎提交 Issue 或者 Pull Request。

## 许可证

该工具使用 MIT 许可证。详情请参阅 LICENSE 文件。
