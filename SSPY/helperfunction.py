import sys
import os
import platform
import threading


def clean_enter(in_list: list | tuple | str, inst_None) -> list | str:
    """
    清除in_sheet中的\\n，返回一个list[list]
    Args:
        in_list:输入的list
        inst_None:用什么参数来替换in_list中的None
    """
    out_list = []
    if in_list is None:
        return inst_None
    elif isinstance(in_list, str):
        return in_list.replace('\n', '').replace('\r', '')
    elif isinstance(in_list, list | tuple):
        for row in in_list:
            out_list.append(clean_enter(row, inst_None))
    return out_list


def clean_space(in_list: list | tuple | str,inst_None) -> list | str:
    out_list = []
    if in_list is None:
        return inst_None
    elif isinstance(in_list, str):
        return in_list.replace(' ', '')
    elif isinstance(in_list, list | tuple):
        for row in in_list:
            out_list.append(clean_space(row,inst_None))
    return out_list


def _exit(in_flag: threading.Event | None) -> bool:
    """退出方法，检测进程flag是否标志为set"""
    if isinstance(in_flag, threading.Event):
        if in_flag.is_set():
            return True
    return False

# def clear_console():
#     # 判断操作系统
#     if platform.system() == "Windows":
#         os.system("cls")  # Windows 系统使用 cls 命令
#     else:
#         os.system("clear")  # Linux/macOS 系统使用 clear 命令
#
#
# def press_any_key_to_continue(prompt = "按回车键继续..."):
#     """
#     按任意键继续功能，支持 Windows/macOS/Linux
#     :param prompt: 提示文本，默认“按任意键继续...”
#     """
#     print('\n')
#     print(prompt, end = "", flush = True)  # 不换行输出提示，flush=True 确保即时显示
#     input()
#     print()  # 按键后换行，避免后续输出与提示重叠
