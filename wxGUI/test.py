import wx

# 创建应用实例
app = wx.App()

# 创建窗口
frame = wx.Frame(None, title = "wxPython 测试", size = (400, 300))
frame.Show(True)  # 显示窗口

# 启动事件循环
app.MainLoop()
