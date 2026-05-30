# 启动代理文件，调用子文件夹里的主程序
import sys
from pathlib import Path

# 把bazi文件夹加入Python路径
sys.path.append(str(Path(__file__).parent / "bazi"))

# 运行子文件夹里的APP.py
exec(open("bazi/APP.py", encoding="utf-8").read())
