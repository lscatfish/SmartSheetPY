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


def clear_console():
    # 判断操作系统
    if platform.system() == "Windows":
        os.system("cls")  # Windows 系统使用 cls 命令
    else:
        os.system("clear")  # Linux/macOS 系统使用 clear 命令


def press_any_key_to_continue(prompt = "按任意键继续..."):
    """
    按任意键继续功能，支持 Windows/macOS/Linux
    :param prompt: 提示文本，默认“按任意键继续...”
    """
    print('\n')
    print(prompt, end = "", flush = True)  # 不换行输出提示，flush=True 确保即时显示
    try:
        # Windows 系统
        if os.name == "nt":
            import msvcrt
            msvcrt.getch()  # 读取任意键（无需回车），忽略回车键的二次触发
        # Linux/macOS 系统
        else:
            import tty
            import termios
            # 保存终端原有配置
            old_settings = termios.tcgetattr(sys.stdin)
            try:
                # 设置终端为“立即读取”模式（无需回车）
                tty.setraw(sys.stdin.fileno())
                sys.stdin.read(1)  # 读取 1 个字符（任意键）
            finally:
                # 恢复终端原有配置（避免终端异常）
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
    except Exception as e:
        # 异常情况下降级为“按回车键继续”
        input(f"\n\n读取键盘输入失败，按回车键继续...（错误：{str(e)}）")
    print()  # 按键后换行，避免后续输出与提示重叠
