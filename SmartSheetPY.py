print('加载资源中...')
import paddlex_hijack
from SSPY.helperfunction import press_any_key_to_continue

"""调用一个a，避免idea把第一行优化删除"""
a = paddlex_hijack.a

import io
import os
import sys

os.system('chcp 65001')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding = 'utf-8', line_buffering = True)
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding = 'utf-8', line_buffering = True)

from QingziClass.doqingziclass import DoQingziClass

qc = DoQingziClass()
qc.start()
print()
press_any_key_to_continue('程序结束，请按任意键退出...')
