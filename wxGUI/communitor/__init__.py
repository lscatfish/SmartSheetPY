# msg_comm/__init__.py
from .core import register_main_process, msg  # 暴露API，简化导入
import threading
from .core import _main_listener  # 导入监听函数

# 自动启动主线程监听循环（仅启动一次）
# 用一个标志确保监听线程不被重复启动
_listener_started = False


def _start_listener():
    """导入自动启动监听函数"""
    global _listener_started
    if not _listener_started:
        # 启动监听线程（守护线程，主程序退出时自动结束）
        threading.Thread(target = _main_listener, daemon = True).start()
        _listener_started = True
        # print("msg_comm 初始化：监听线程已启动")


# 包被导入时自动执行初始化
_start_listener()

# 可选：定义包的版本等元信息
__version__ = "0.1.0"
