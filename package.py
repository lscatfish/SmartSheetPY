"""
打包脚本
"""
import asyncio
from pathlib import Path

import paddlex
import importlib.metadata
import argparse
import subprocess
import sys


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


def compile_module(module):
    # 1. 检查模块是否有 __file__ 属性（内置模块无此属性）
    if not hasattr(module, '__file__'):
        print("模块为内置模块，无 .py 文件，无法获取 .pyc 路径")
        return False
    target_file = Path(module.__file__)
    # 确保路径是 .py 文件（排除 .pyc 等其他文件）
    if target_file.suffix != '.py':
        print(f"模块文件 {target_file} 不是 .py 文件，无法获取 .pyc 路径")
        return False
    print(f'编译文件 {target_file}')
    try:
        _cmd = [
            'python',  # 当前 Python 解释器路径（确保与打包环境一致）
            "-m",
            "compileall",
            str(target_file)
        ]
        # 4. 执行命令并捕获输出
        print(f"执行命令：{' '.join(_cmd)}")
        result = subprocess.run(
            _cmd,
            check = True,  # 若命令执行失败（返回非0状态码），抛出 CalledProcessError
            stdout = subprocess.PIPE,  # 捕获标准输出
            stderr = subprocess.PIPE,  # 捕获标准错误
            text = True  # 输出为字符串格式（而非 bytes）
        )
        # 5. 打印执行结果
        print("编译成功！输出信息：")
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"命令执行失败！错误码：{e.returncode}")
        print(f"错误输出：{e.stderr}")
    except Exception as e:
        print(f"发生异常：{str(e)}")
    return False


if compile_module(asyncio.windows_utils):
    print("开始执行打包逻辑...")
    # 这里添加你的打包代码（如调用 PyInstaller 等）
else:
    print("编译失败，终止打包流程")
    sys.exit(-1)

parser = argparse.ArgumentParser()
parser.add_argument('--file', required = True, help = 'Your file name, e.g. main.py.')
parser.add_argument('--nvidia', action = 'store_true', help = 'Include NVIDIA CUDA and cuDNN dependencies.')

args = parser.parse_args()

main_file = args.file

user_deps = [dist.metadata["Name"] for dist in importlib.metadata.distributions()]
deps_all = list(paddlex.utils.deps.DEP_SPECS.keys())
deps_need = [dep for dep in user_deps if dep in deps_all]

cmd = [
    "pyinstaller", main_file, "--windowed",
    "--collect-data", "paddlex",
    "--collect-binaries", "paddle",
    # 补充 Cython 依赖（根据之前的报错）
    "--add-data", sys.base_prefix + "\\Lib\\site-packages\\Cython\\Utility;Cython/Utility",
    "--add-data", get_module_pyc_path(asyncio.windows_utils) + ";runtime/asyncio",
]

if args.nvidia:
    cmd += ["--collect-binaries", "nvidia"]

for dep in deps_need:
    cmd += ["--copy-metadata", dep]

print("PyInstaller command:", " ".join(cmd))

try:
    result = subprocess.run(cmd, check = True)
except subprocess.CalledProcessError as e:
    print("Installation failed:", e)
    sys.exit(1)
