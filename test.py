# 消息框(wx.MessageBox)

import wx


class SampleMessageBox(wx.Frame):

    def __init__(self, *args, **kw):
        super(SampleMessageBox, self).__init__(*args, **kw)
        self.InitUi()

    def InitUi(self):
        # 延迟3秒后调用self.ShowMessage
        wx.CallLater(300, self.ShowMessage)

        self.SetTitle("实战wxPython: 消息框")
        self.SetSize(400, 280)
        self.Centre()

    def ShowMessage(self):
        r= wx.MessageBox("下载完毕\n下载完毕\n\n\n\n\n\n\nvjfdvjfvnvf\n\n\n\nfbuisvefvb\nvfsvsf\nfbsf", "信息", wx.OK | wx.ICON_INFORMATION | wx.CANCEL,x=300,y=300)
        match r:
            case wx.OK:
                print('OK')
            case wx.CANCEL:
                print('CANCEL')
            case wx.ID_ABORT:
                print('ABORT')


def main():
    app = wx.App()
    sample = SampleMessageBox(None)
    sample.Show()
    app.MainLoop()


if __name__ == "__main__":
    main()
