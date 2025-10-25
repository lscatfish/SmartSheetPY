"""标准文件库，用于控制文件的收集与解析"""


def _set_BASE_DIR():
    import os
    bd = os.getcwd()
    return bd

BASE_DIR = _set_BASE_DIR()
