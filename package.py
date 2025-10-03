"""
打包脚本
编译windows_utils.py为windows_utils.pyc，exe直接使用pyc文件，防止了
"""

import paddlex
import importlib.metadata
import argparse
import subprocess
import sys


def compile_windows_utils():
    """编译windows_utils.py文件为.pyc"""
    print('编译windows_utils.py文件...')
    try:
        target_file = sys.base_prefix + "\\Lib\\asyncio\\windows_utils.py"
        _cmd = [
            'python',  # 当前 Python 解释器路径（确保与打包环境一致）
            "-m",
            "compileall",
            "-b",  # 保留源文件，仅生成 .pyc 文件
            target_file
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


if compile_windows_utils():
    print("开始执行打包逻辑...")
    # 这里添加你的打包代码（如调用 PyInstaller 等）
else:
    print("编译失败，终止打包流程")
    sys.exit(1)

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
    # "--hidden-import", "asyncio.windows_utils",
    "--add-data", sys.base_prefix + "\\Lib\\asyncio\\windows_utils.pyc;runtime/asyncio",
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
