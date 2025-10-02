def clean_enter(in_list: list | tuple) -> list:
    """清除in_sheet中的\\n，返回一个list[list]"""
    out_list = []
    if in_list is None: return out_list
    for row in in_list:
        if isinstance(row, list | tuple):
            out_list.append(clean_enter(row))
        else:
            c = str(row)
            nc = c.replace('\n', '').replace('\r', '')
            out_list.append(nc)
    return out_list


import os
import platform

def clear_console():
    # 判断操作系统
    if platform.system() == "Windows":
        os.system("cls")  # Windows 系统使用 cls 命令
    else:
        os.system("clear")  # Linux/macOS 系统使用 clear 命令
