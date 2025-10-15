# 这是[SmartSheet](https://github.com/lscatfish/SmartSheet)的python版本

## 你任何的联网访问都必须严格遵守互联网机器人规范

## 🚀 快速开始

我们推荐你从官网开始：
```commandline
git clone https://github.com/lscatfish/SmartSheetPY.git
```
国内镜像（我们不推荐，24h更新一次）：
```commandline
git clone https://gitcode.com/lscatfish/SmartSheetPY.git
```







### 依赖

- Paddle v3.2.0
`pip install paddleocr[all] -i https://pypi.tuna.tsinghua.edu.cn/simple`
此命令会自动安装`opencv`以及其他部分依赖
- opencv v4.1  
`pip install opencv-python -i https://pypi.tuna.tsinghua.edu.cn/simple`
- openpyxl v1.6.1  
`pip install openpyxl -i https://pypi.tuna.tsinghua.edu.cn/simple`
- python-docx v1.2.0  
`pip install python-docx -i https://pypi.tuna.tsinghua.edu.cn/simple`
- pdfplumber v0.11.7  
`pip install pdfplumber -i https://pypi.tuna.tsinghua.edu.cn/simple`
- PyMuPDF v1.26.5  
`pip install PyMuPDF -i https://pypi.tuna.tsinghua.edu.cn/simple`
- pyinstaller v6.16.0  
`pip install pyinstaller -i https://pypi.tuna.tsinghua.edu.cn/simple`
- numpy v2.3.3

## 测试数据集
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;考虑率到测试数据包含极为敏感的个人信息，若实在需要测试数据，请联系[lscatfish](https://github.com/lscatfish)  

## TODO 
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;使用`opencv`的自带算法开发一个自动进行透视校正+手动透视校正的模块。  
**不得不指出，使用python打包产生的程序包会占用很多空间，并且运行效率低下。**   
**可以修改打包文件[package.py](./package.py)来移除非必要的包，以提高运行效率。**



# 一些必要的重新定向（hijack）

<details>
<summary style="font-size: 20px; font-weight: bold;">关于劫持paddleOCR的下载器的方法</summary>

- [x] 拉取运行目录（我们不推荐你在非`.exe`目录使用`./path/to/your/SmartSheetALL.exe`或是`./path/to/your/SmartSheetPY.exe`），这会让程序错误的识别目录。
- [x] 将模型地址重新定向到`MY_MIRROR_ROOT`（顺便创建文件夹）。
- [x] 修改全部的默认环境变量与默认目录。
- [x] 强制给所有`hoster`类打补丁，让它们的`save_dir = MY_MIRROR_ROOT`
- [x] 


```python
import os
import pathlib

# ========== 1. 你想把模型放在哪里 ==========
BASE_DIR = os.getcwd()
MY_MIRROR_ROOT = pathlib.Path(BASE_DIR) / "official_models"
MY_MIRROR_ROOT.mkdir(parents = True, exist_ok = True)

# ========== 2. 把环境变量、默认目录全部改掉 ==========
os.environ["PADDLE_PDX_CACHE_HOME"] = str(BASE_DIR)

from paddlex.inference.utils.official_models import (
    _ModelManager,
    _BosModelHoster,
    _HuggingFaceModelHoster,
    _ModelScopeModelHoster,
    _AIStudioModelHoster,
)

_ModelManager._save_dir = MY_MIRROR_ROOT  # 新生成的 Manager 会用到

# ========== 3. 强制给所有 hoster 类打补丁，让它们的 save_dir=MY_MIRROR_ROOT ==========
for hoster_cls in (
        _BosModelHoster,
        _HuggingFaceModelHoster,
        _ModelScopeModelHoster,
        _AIStudioModelHoster,
):
    # 把 __init__ 里 self._save_dir = save_dir 改成 self._save_dir = MY_MIRROR_ROOT
    _orig_init = hoster_cls.__init__


    def _new_init(self, save_dir, *, __orig_init = _orig_init):
        __orig_init(self, MY_MIRROR_ROOT)  # 硬塞我们的目录


    hoster_cls.__init__ = _new_init


# ========== 4. 劫持 _ModelManager._get_model_local_path，仍复用官方 _get_model_local_path ==========
def _hijacked_get_model_local_path(self, model_name: str) -> pathlib.Path:
    target_dir = MY_MIRROR_ROOT / model_name
    # 本地命中
    if target_dir.exists() and (target_dir / "inference.yml").exists():
        return target_dir
    # 缺失 → 复用官方“挑最优 hoster + 下载”逻辑

    """这里应该加上一个选择位置"""
    """添加一个注册函数，将hijack的路径定向到镜像目录中"""

    return self._download_from_hoster(self._hosters, model_name)


_ModelManager._get_model_local_path = _hijacked_get_model_local_path
a: int = 0
```

</details>


<details>
<summary style="font-size: 20px; font-weight: bold;">关于劫持paddleOCR子线程的方法</summary>

这是因为在打包生成的程序运行时，加载模型ppocr的时候会出现闪窗
这里我已经修复了，直接执行打包命令 `python ./package.py --file ./SmartSheetPY.py`即可。  
如果你要运行多文件打包程序（包含`EmailDownloader.py`与`ToolSearchingMain.py`），请使用`build`目录下的`SmartSheetALL.spec`文件： 
`pyinstaller SmartSheetALL.spec`

以下是我的解决代码：  
在程序的头部插入如下代码，在打包的时候接管ppocr的子模块

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

```textmate
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
import sys, os, importlib.util, subprocess

# 仅 PyInstaller 打包后才执行外置加载
if getattr(sys, 'frozen', False) and sys.platform == 'win32':
    pyc_path = os.path.join(sys._MEIPASS, 'runtime', 'asyncio', 'windows_utils.pyc')
    spec = importlib.util.spec_from_file_location("asyncio.windows_utils", pyc_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    sys.modules['asyncio.windows_utils'] = mod  # 阻断 PyInstaller 再解析

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
</details>   
    



-----   

-----   

-----   

# 图片解析方式
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;本项目使用飞桨开发的文字识别库PaddleOCR其下的子模块`PP-SructureV3`的子产线`通用表格识别V2`，启用其所有功能。 [PP-StructureV3官方教程](http://www.paddleocr.ai/latest/version3.x/pipeline_usage/PP-StructureV3.html#1-pp-structurev3) &nbsp;&nbsp; [table_recognition_v2官方教程](http://www.paddleocr.ai/latest/version3.x/pipeline_usage/table_recognition_v2.html)   
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
飞桨自`PPOCR-v3.2.0`开始更换了预训练模型的构架，并且在没有指定模型地址的情况下会从官网自动下载`config/*.yaml`文件中配置
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;值得说明的是，`表格识别V2`模块对稍微倾斜的表格的识别结果排列顺序存在严重bug，会出现行单元格数据未按照照片的规律排列的现象（但是排列顺序呈现出回环现象）。   
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;针对这一问题，要对识别出的学号对每一行的文本进行重新定位，在脚本[myimg.py](./SSPY/myimg.py)函数`rotation_checklist_content`中对此功能进行了实现。
