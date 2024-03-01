#!/bin/sh

# 检查是否设置了 TEST 环境变量
if [ "$TEST" = "YES" ]; then
  echo "Running in test mode"
  # 这里执行测试模式相关的命令
  python /app/test_app.py
else
  echo "Running in normal mode"

  # 无限循环，确保在 app.py 异常退出时能重新启动
  while true; do
    python app.py
    echo "app.py 异常退出，正在重新启动..."
    sleep 1  # 可以根据需要调整等待时间
  done
fi
