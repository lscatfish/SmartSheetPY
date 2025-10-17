"""入口文件"""

import sys, os, importlib.util, subprocess

# 仅 PyInstaller 打包后才执行外置加载
if getattr(sys, 'frozen', False) and sys.platform == 'win32':
    pyc_path = os.path.join(sys._MEIPASS, 'runtime', 'asyncio', f'windows_utils.cpython-{sys.version_info.major}{sys.version_info.minor}.pyc')
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


#-----------------------------------正常入口-------------------------------------------#

from wxGUI.SSPYframe import SSPYMainFrame
from wx import App


app = App()
from QingziClass.doqingziclass import DoQingziClass

SSPYMainFrame(None, title = "SmartSheetPY", QC = DoQingziClass())
app.MainLoop()


# os.system('chcp 65001')
# sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding = 'utf-8', line_buffering = True)
# sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding = 'utf-8', line_buffering = True)
