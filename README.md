# 这是[SmartSheet](https://github.com/lscatfish/SmartSheet)的python版本

## 依赖

- Paddle v3.2.0 &nbsp;&nbsp;&nbsp;
- opencv v4.1 &nbsp;&nbsp;&nbsp;
- openpyxl v1.6.1 &nbsp;&nbsp;&nbsp;
- python-docx v1.2.0
- pypdfium2 v4.30.0
- pdfplumber v0.11.7
- pyinstaller v6.16.0
- python v3.10
- numpy v2.3.3

### 不得不指出，使用python打包产生的程序包会占用很多空间，并且运行效率低下

### 可以修改打包文件[package.py](./package.py)来移除非必要的包，以追求运行效率

## 关于劫持paddle子线程的方法

这是因为在打包生成的程序运行时，加载模型ppocr的时候会出现闪窗
这里我已经修复了，直接执行打包命令 `python ./package.py --file ./SmartSheetPY.py`即可。

以下是我的解决代码：  
在程序的头部插入如下代码，接管ppocr的子模块

`````python
import subprocess
import sys
import os

if sys.platform == 'win32' and getattr(sys, 'frozen', False):  # 只在打包后生效
    _old_popen = subprocess.Popen


    def _no_console_popen(*args, **kwargs):
        # 强制隐藏控制台窗口
        si = subprocess.STARTUPINFO()
        si.dwFlags = subprocess.STARTF_USESHOWWINDOW
        si.wShowWindow = subprocess.SW_HIDE
        kwargs['startupinfo'] = si
        kwargs.setdefault('creationflags', 0)
        kwargs['creationflags'] |= subprocess.CREATE_NO_WINDOW
        return _old_popen(*args, **kwargs)


    subprocess.Popen = _no_console_popen
`````

此方法最简单，但是在使用`pyinstaller`打包的时候会出错。  
这是`PyInstaller 5.13+`与`Python 3.11+`的已知兼容 bug：
`asyncio\windows_utils.py`里用`ctypes.WINFUNCTYPE`动态创建函数时，`PyInstaller`的importer把`code`对象误当成`str`，导致
`TypeError: function() argument 'code' must be code, not str`。

不兼容的bug如下在打包之后运行`.exe`会输出一下错误：

```
[22:58:29] Exception in thread Thread-1 (__worker):
[22:58:29] Traceback (most recent call last):
[22:58:29]   File "threading.py", line 1043, in _bootstrap_inner
[22:58:29]   File "threading.py", line 994, in run
[22:58:29]   File "wxGUI\myframe.py", line 58, in __worker
[22:58:29]   File "<frozen importlib._bootstrap>", line 1360, in _find_and_load
[22:58:29]   File "<frozen importlib._bootstrap>", line 1331, in _find_and_load_unlocked
[22:58:29]   File "<frozen importlib._bootstrap>", line 935, in _load_unlocked
[22:58:29]   File "pyimod02_importers.py", line 457, in exec_module
[22:58:29]   File "wxGUI\hijack_paddlex.py", line 19, in <module>
[22:58:29]   File "<frozen importlib._bootstrap>", line 1360, in _find_and_load
[22:58:29]   File "<frozen importlib._bootstrap>", line 1331, in _find_and_load_unlocked
[22:58:29]   File "<frozen importlib._bootstrap>", line 935, in _load_unlocked
[22:58:29]   File "pyimod02_importers.py", line 457, in exec_module
[22:58:29]   File "paddlex\__init__.py", line 41, in <module>
[22:58:29]   File "paddlex\__init__.py", line 26, in _initialize
[22:58:29]   File "<frozen importlib._bootstrap>", line 1360, in _find_and_load
[22:58:29]   File "<frozen importlib._bootstrap>", line 1331, in _find_and_load_unlocked
[22:58:29]   File "<frozen importlib._bootstrap>", line 935, in _load_unlocked
[22:58:29]   File "pyimod02_importers.py", line 457, in exec_module
[22:58:29]   File "paddlex\repo_manager\__init__.py", line 16, in <module>
[22:58:29]   File "<frozen importlib._bootstrap>", line 1360, in _find_and_load
[22:58:29]   File "<frozen importlib._bootstrap>", line 1331, in _find_and_load_unlocked
[22:58:29]   File "<frozen importlib._bootstrap>", line 935, in _load_unlocked
[22:58:29]   File "pyimod02_importers.py", line 457, in exec_module
[22:58:29]   File "paddlex\repo_manager\core.py", line 20, in <module>
[22:58:29]   File "<frozen importlib._bootstrap>", line 1360, in _find_and_load
[22:58:29]   File "<frozen importlib._bootstrap>", line 1331, in _find_and_load_unlocked
[22:58:29]   File "<frozen importlib._bootstrap>", line 935, in _load_unlocked
[22:58:29]   File "pyimod02_importers.py", line 457, in exec_module
[22:58:29]   File "paddlex\repo_manager\repo.py", line 25, in <module>
[22:58:29]   File "<frozen importlib._bootstrap>", line 1360, in _find_and_load
[22:58:29]   File "<frozen importlib._bootstrap>", line 1331, in _find_and_load_unlocked
[22:58:29]   File "<frozen importlib._bootstrap>", line 935, in _load_unlocked
[22:58:29]   File "pyimod02_importers.py", line 457, in exec_module
[22:58:29]   File "paddlex\utils\file_interface.py", line 22, in <module>
[22:58:29]   File "<frozen importlib._bootstrap>", line 1360, in _find_and_load
[22:58:29]   File "<frozen importlib._bootstrap>", line 1331, in _find_and_load_unlocked
[22:58:29]   File "<frozen importlib._bootstrap>", line 935, in _load_unlocked
[22:58:29]   File "pyimod02_importers.py", line 457, in exec_module
[22:58:29]   File "filelock\__init__.py", line 20, in <module>
[22:58:29]   File "<frozen importlib._bootstrap>", line 1360, in _find_and_load
[22:58:29]   File "<frozen importlib._bootstrap>", line 1331, in _find_and_load_unlocked
[22:58:29]   File "<frozen importlib._bootstrap>", line 935, in _load_unlocked
[22:58:29]   File "pyimod02_importers.py", line 457, in exec_module
[22:58:29]   File "filelock\asyncio.py", line 5, in <module>
[22:58:29]   File "<frozen importlib._bootstrap>", line 1360, in _find_and_load
[22:58:29]   File "<frozen importlib._bootstrap>", line 1331, in _find_and_load_unlocked
[22:58:29]   File "<frozen importlib._bootstrap>", line 935, in _load_unlocked
[22:58:29]   File "pyimod02_importers.py", line 457, in exec_module
[22:58:29]   File "asyncio\__init__.py", line 43, in <module>
[22:58:29]   File "<frozen importlib._bootstrap>", line 1360, in _find_and_load
[22:58:29]   File "<frozen importlib._bootstrap>", line 1331, in _find_and_load_unlocked
[22:58:29]   File "<frozen importlib._bootstrap>", line 935, in _load_unlocked
[22:58:29]   File "pyimod02_importers.py", line 457, in exec_module
[22:58:29]   File "asyncio\windows_events.py", line 26, in <module>
[22:58:29]   File "<frozen importlib._bootstrap>", line 1360, in _find_and_load
[22:58:29]   File "<frozen importlib._bootstrap>", line 1331, in _find_and_load_unlocked
[22:58:29]   File "<frozen importlib._bootstrap>", line 935, in _load_unlocked
[22:58:29]   File "pyimod02_importers.py", line 457, in exec_module
[22:58:29]   File "asyncio\windows_utils.py", line 125, in <module>
[22:58:29] TypeError: function() argument 'code' must be code, not str
```

### 修复这个bug：

`TypeError: function() argument 'code' must be code, not str`本质是`asyncio.windows_utils`在`冻结（frozen）`环境下动态生成
`ctypes`回调，
而`PyInstaller`的`importer`把`code`对象误当`str`。
官方已合并补丁，只需 **把有问题的模块打成“隐藏导入 + 二进制收集”** 即可绕过。

#### 我的修复方案：

首先运行`python -m compileall -b "%PYTHONHOME%\Lib\asyncio\windows_utils.py"`会在同级目录得到`windows_utils.pyc`

在你的`.spec`文件里的`datas`中加入`(sys.base_prefix + "\\Lib\\asyncio\\windows_utils.pyc", 'runtime/asyncio'),`
```pycon
# -*- mode: python ; coding: utf-8 -*-
a = Analysis(
    ...
    datas=[
        (sys.base_prefix + "\\Lib\\asyncio\\windows_utils.pyc", 'runtime/asyncio'),
    ],
    ...
)
```
在`SmartSheetPY.py`的头部加上以下代码，只在`pyinstall`的时候运行：
```python
# main.py  最顶部（任何 import asyncio 之前）
import sys, os, importlib.util

# 仅 PyInstaller 打包后才执行外置加载
if getattr(sys, 'frozen', False) and sys.platform == 'win32':
    pyc_path = os.path.join(sys._MEIPASS, 'runtime', 'asyncio', 'windows_utils.pyc')
    spec = importlib.util.spec_from_file_location("asyncio.windows_utils", pyc_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    sys.modules['asyncio.windows_utils'] = mod   # 阻断 PyInstaller 再解析
```
最后执行`pyinstall -w SmartSheetPY.spec`

当然，我已经完成了打包文件：
[SmartSheetPY.py](./SmartSheetPY.py)头部添加
```python
import sys, os, importlib.util
# 仅 PyInstaller 打包后才执行外置加载
if getattr(sys, 'frozen', False) and sys.platform == 'win32':
    pyc_path = os.path.join(sys._MEIPASS, 'runtime', 'asyncio', 'windows_utils.pyc')
    spec = importlib.util.spec_from_file_location("asyncio.windows_utils", pyc_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    sys.modules['asyncio.windows_utils'] = mod   # 阻断 PyInstaller 再解析

import subprocess
import sys
import os

if sys.platform == 'win32' and getattr(sys, 'frozen', False):  # 只在打包后生效
    _old_popen = subprocess.Popen

    def _no_console_popen(*args, **kwargs):
        # 强制隐藏控制台窗口
        si = subprocess.STARTUPINFO()
        si.dwFlags = subprocess.STARTF_USESHOWWINDOW
        si.wShowWindow = subprocess.SW_HIDE
        kwargs['startupinfo'] = si
        kwargs.setdefault('creationflags', 0)
        kwargs['creationflags'] |= subprocess.CREATE_NO_WINDOW
        return _old_popen(*args, **kwargs)

    subprocess.Popen = _no_console_popen
```

[package.py](./package.py) 对ppocr相关文件打包之前添加编译`windows_utils.py`的文件。cmd中加入`"--add-data", sys.base_prefix + "\\Lib\\asyncio\\windows_utils.pyc;runtime/asyncio",`
```python
import sys,subprocess
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
```

