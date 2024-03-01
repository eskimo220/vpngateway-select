#!/bin/sh

# 无限循环，确保在 app.py 异常退出时能重新启动
while true; do
    python app.py
    echo "app.py 异常退出，正在重新启动..."
    sleep 1  # 可以根据需要调整等待时间
done

