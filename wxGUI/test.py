import wx
import os

APP_EXIT = 1


class Example(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(Example, self).__init__(*args, **kwargs)

        self.SetTitle('实战wxPython: 为菜单栏添加快捷键和图标')
        self.SetSize(400, 300)

        self.InitUi()

        self.Centre()

    def InitUi(self):
        menubar = wx.MenuBar()
        fileMenu = wx.Menu()
        qmi = wx.MenuItem(fileMenu, APP_EXIT, '退出(&Q)\tCtrl+Q')
        # qmi.SetBitmap(wx.Bitmap(os.path.dirname(__file__) + '/exit.png'))
        fileMenu.Append(qmi)

        # 绑定菜单项的行为
        self.Bind(wx.EVT_MENU, self.OnQuit, id = APP_EXIT)

        menubar.Append(fileMenu, '文件(&F)')
        self.SetMenuBar(menubar)

    def OnQuit(self, e):
        self.Close()


def main():
    app = wx.App()
    window = Example(None)
    window.Show()
    app.MainLoop()


if __name__ == '__main__':
    main()
