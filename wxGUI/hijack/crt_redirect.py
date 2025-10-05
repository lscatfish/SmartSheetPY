# crt_redirect.py
"""
劫持 Windows C 运行时 stderr，使其输出重定向到 wx 消息窗口
无控制台（PyInstaller -w）下也不会弹框 / 乱码
"""
import os
import sys
import threading
import msvcrt
import ctypes
from ctypes import wintypes
from wxGUI.text_hub import postText  # 统一发消息入口

import re



def strip_ansi(text):
    """清除ANSI转移序列"""
    ANSI_RE = re.compile(r'\x1b\[[0-9;]*m')  # 匹配 \x1b[...m
    return ANSI_RE.sub('', text)


a = 0
# -------------------- Win32 原型声明 --------------------
kernel32 = ctypes.windll.kernel32


class SECURITY_ATTRIBUTES(ctypes.Structure):
    _fields_ = [("nLength", wintypes.DWORD),
                ("lpSecurityDescriptor", wintypes.LPVOID),
                ("bInheritHandle", wintypes.BOOL)]

    def __init__(self):
        self.nLength = ctypes.sizeof(self)


# CreatePipe
kernel32.CreatePipe.argtypes = [
    ctypes.POINTER(wintypes.HANDLE),  # hReadPipe
    ctypes.POINTER(wintypes.HANDLE),  # hWritePipe
    ctypes.POINTER(SECURITY_ATTRIBUTES),  # lpPipeAttributes
    wintypes.DWORD  # nSize
]
kernel32.CreatePipe.restype = wintypes.BOOL

# SetStdHandle
kernel32.SetStdHandle.argtypes = [wintypes.DWORD, wintypes.HANDLE]
kernel32.SetStdHandle.restype = wintypes.BOOL

STD_ERROR_HANDLE = -12


# -------------------- 核心逻辑 --------------------
def _redirect_crt_stderr():
    """把 Windows CRT stderr 重定向到匿名管道，后台线程实时读"""
    read_h = wintypes.HANDLE()
    write_h = wintypes.HANDLE()
    sa = SECURITY_ATTRIBUTES()

    # 1. 创建匿名管道
    if not kernel32.CreatePipe(ctypes.byref(read_h), ctypes.byref(write_h), sa, 0):
        return

    # 2. 让 CRT 用管道写端当 stderr
    kernel32.SetStdHandle(STD_ERROR_HANDLE, write_h)

    # 3. Python 的 stderr 也指过去（可选）
    sys.stderr = os.fdopen(msvcrt.open_osfhandle(write_h.value, 0), 'w', buffering = 1)

    # 4. 后台线程读管道
    def _reader():
        read_fd = msvcrt.open_osfhandle(read_h.value, 0)
        with os.fdopen(read_fd, 'r', encoding = 'utf-8', errors = 'replace') as f:
            while True:
                line = f.readline()
                if not line:
                    break
                clean = strip_ansi(line).rstrip('\n')
                if clean:
                    postText(clean, color = 'default')

    threading.Thread(target = _reader, daemon = True).start()


# -------------------- 自动生效（仅 Windows） --------------------
if sys.platform == 'win32':
    _redirect_crt_stderr()
