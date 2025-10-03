import sys
import os
import platform


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
