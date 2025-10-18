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


def clean_space(in_list: list | tuple | str, inst_None) -> list | str:
    out_list = []
    if in_list is None:
        return inst_None
    elif isinstance(in_list, str):
        return in_list.replace(' ', '')
    elif isinstance(in_list, list | tuple):
        for row in in_list:
            out_list.append(clean_space(row, inst_None))
    return out_list


def _exit(in_flag: threading.Event | None) -> bool:
    """退出方法，检测进程flag是否标志为set"""
    if isinstance(in_flag, threading.Event):
        if in_flag.is_set():
            return True
    return False


def sort_table(
    in_table: list[list[str]],
    CompareMethod = lambda a, b: a < b,
    exclude_rows: list[int] = None,
    exclude_cols: list[int] = None, ):
    """
    对一个矩形表格进行排序
    Args:
        in_table:输入的表格
        CompareMethod:自定义的比较方法（lambda函数）
        exclude_rows:排除的行
        exclude_cols:排除的列
    """

    def pre(exc: list[int], len_max: int):
        """预处理，产生参与比较的行与列"""
        inc: list[int] = []
        for i in range(len_max):
            if isinstance(exc, list) and (i in exc):
                continue
            inc.append(i)
        return inc

    len_rows = len(in_table)
    """行数"""
    len_cols = len(in_table[0])
    """列数"""
    include_rows = pre(exclude_rows, len_rows)
    """参与比较的行号"""
    include_cols = pre(exclude_cols, len_cols)
    """参与比较的列号"""

    # 启动比较程序
    for i in include_rows:
        for j in include_rows:
            if i <= j: continue
            if CompareMethod(in_table[i], in_table[j]):
                for k in include_cols:
                    in_table[j][k], in_table[i][k] = in_table[i][k], in_table[j][k]
