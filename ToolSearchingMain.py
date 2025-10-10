"""搜索器入口"""

from wx import App
from wxGUI.TSframe import TSMainFrame



if __name__ == '__main__':
    app = App()
    TSMainFrame(None, title = "TS")
    app.MainLoop()
