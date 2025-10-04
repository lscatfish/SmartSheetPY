import asyncio
import sys
from pathlib import Path


def get_module_pyc_path(module):
    """
    通过模块对象获取其编译后的 .pyc 文件路径

    参数：
        module: 已导入的模块对象（如 import asyncio.windows_utils 后的模块）
    返回：
        Path: .pyc 文件的完整路径；若无法获取则返回 None
    """
    # 1. 检查模块是否有 __file__ 属性（内置模块无此属性）
    if not hasattr(module, '__file__'):
        print("模块为内置模块，无 .py 文件，无法获取 .pyc 路径")
        return None

    # 2. 获取 .py 文件路径，并转换为 Path 对象
    py_path = Path(module.__file__)
    # 确保路径是 .py 文件（排除 .pyc 等其他文件）
    if py_path.suffix != '.py':
        print(f"模块文件 {py_path} 不是 .py 文件，无法获取 .pyc 路径")
        return None

    # 3. 确定 __pycache__ 目录路径（.py 文件所在目录的子文件夹）
    pycache_dir = py_path.parent / '__pycache__'

    # 4. 生成 .pyc 文件名（格式：模块名.解释器标识-版本号.pyc）
    # 4.1 获取模块名（取最后一级，如 asyncio.windows_utils → windows_utils）
    module_name = module.__name__.split('.')[-1]
    # 4.2 获取解释器标识（通常为 'cpython'，即官方 C 实现）
    interpreter_id = 'cpython'
    # 4.3 获取版本号（如 3.13 → '313'）
    version = f"{sys.version_info.major}{sys.version_info.minor}"
    # 4.4 拼接完整文件名
    pyc_filename = f"{module_name}.{interpreter_id}-{version}.pyc"

    # 5. 拼接 .pyc 文件的完整路径
    pyc_path = pycache_dir / pyc_filename

    return str(pyc_path)

print(get_module_pyc_path(asyncio.windows_utils))
