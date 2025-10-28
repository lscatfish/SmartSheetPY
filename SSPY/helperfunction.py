# -*- coding: utf-8 -*-

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


def all_str(in_list: list | tuple | str, instr_None: str = '') -> str:
    """融合所有的str"""
    outstr = ''
    if in_list is None:
        return instr_None
    elif isinstance(in_list, str):
        return in_list
    elif isinstance(in_list, list | tuple):
        for row in in_list:
            outstr += all_str(row, instr_None)
    return outstr


from threading import Event


def _exit(in_flag: Event | None) -> bool:
    """退出方法，检测进程flag是否标志为set"""
    if isinstance(in_flag, Event):
        if in_flag.is_set():
            return True
    return False


def sort_table(
    in_table: list[list[str]],
    CompareMethod = lambda a, b: a[0] < b[0],
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
            if i >= j: continue
            if CompareMethod(in_table[i], in_table[j]):
                for k in include_cols:
                    in_table[j][k], in_table[i][k] = in_table[i][k], in_table[j][k]


def trans_list_to_str(in_list: list[str]) -> str:
    """
    将输入的in_list转换为str
    Args:
        in_list:输入的list
        auto_enter:自动换行
    """
    out_str = ''
    if not isinstance(in_list, list): return out_str
    len_l = len(in_list)
    if len_l == 0: return out_str
    for i in range(len_l):
        out_str += (in_list[i] + ('\n' if (i + 1) < len_l else ''))
    return out_str


def deduplication_list(in_list: list, dedp):
    """对一个list去重
    Args:
        in_list:输入的list
        dedp:相同判断方法
    """
    pass
