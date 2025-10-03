from wxGUI.myframe import MainFrame
from wx import App


app = App()
from QingziClass.doqingziclass import DoQingziClass
MainFrame(None, title = "SmartSheetPY", QC = DoQingziClass())
app.MainLoop()


# import io
# import os
# import sys
# os.system('chcp 65001')
# sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding = 'utf-8', line_buffering = True)
# sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding = 'utf-8', line_buffering = True)
