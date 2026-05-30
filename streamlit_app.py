# 启动代理文件，调用子文件夹里的主程序
import sys
from pathlib import Path

# 运行bazi文件夹里的APP.py
exec(open("bazi/APP.py", encoding="utf-8").read())
