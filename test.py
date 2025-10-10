import wx


class MyFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title = "进度条示例", size = (600, 400))

        # 创建主面板
        self.main_panel = wx.Panel(self)
        # 主面板使用垂直方向的BoxSizer，便于整体布局
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.main_panel.SetSizer(self.main_sizer)

        # 1. 首先添加一些其他的内容控件（例如一个按钮用于触发操作）到主Sizer，它们会占据面板的上部空间
        self.dummy_button = wx.Button(self.main_panel, label = "开始模拟任务")
        self.main_sizer.Add(self.dummy_button, proportion = 0, flag = wx.EXPAND | wx.ALL, border = 10)
        self.Bind(wx.EVT_BUTTON, self.on_start_task, self.dummy_button)

        # 2. 添加一个“弹簧”，让上面的内容向上顶，进度条相关部分保持在底部
        # proportion=1 意味着这个空间会尽可能多地占据剩余空间
        self.main_sizer.AddStretchSpacer(prop = 1)

        # 3. 创建一个水平Sizer来容纳进度条和其提示文本（它们将作为一个整体位于底部）
        self.bottom_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # 创建进度条 (wx.Gauge)
        # range 参数设定进度条的最大值
        self.progress_gauge = wx.Gauge(self.main_panel, range = 100, size = (-1, 20), style = wx.GA_HORIZONTAL)
        # 创建静态文本用于显示提示
        self.status_text = wx.StaticText(self.main_panel, label = "准备就绪", style = wx.ALIGN_LEFT)

        # 将进度条和状态文本添加到水平Sizer中
        # 进度条占据大部分宽度
        self.bottom_sizer.Add(self.progress_gauge, proportion = 1, flag = wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, border = 5)
        # 状态文本占据固定宽度
        self.bottom_sizer.Add(self.status_text, proportion = 0, flag = wx.ALIGN_CENTER_VERTICAL)

        # 4. 将水平Sizer（包含进度条和文本）添加到主垂直Sizer的底部
        # flag=wx.EXPAND|wx.ALL 让水平Sizer可以扩展宽度，并设置边距
        self.main_sizer.Add(self.bottom_sizer, proportion = 0, flag = wx.EXPAND | wx.ALL, border = 10)

        # 创建一个定时器用于模拟进度更新
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.update_progress, self.timer)
        self.current_progress = 0

        self.Centre()
        self.Show()

    def on_start_task(self, event):
        """点击按钮开始模拟任务"""
        self.current_progress = 0
        self.progress_gauge.SetValue(self.current_progress)
        self.status_text.SetLabelText("任务进行中...")
        # 启动定时器，每100毫秒触发一次更新
        self.timer.Start(100)

    def update_progress(self, event):
        """定时器事件，更新进度条和状态文本"""
        self.current_progress += 1
        self.progress_gauge.SetValue(self.current_progress)

        if self.current_progress >= 100:
            self.timer.Stop()
            self.status_text.SetLabelText("任务完成！")
            # 可选：任务完成后一段时间重置状态
            # wx.CallLater(2000, self.status_text.SetLabelText, "准备就绪")
        else:
            # 更新进度百分比文本
            self.status_text.SetLabelText(f"进度: {self.current_progress}%")


if __name__ == "__main__":
    app = wx.App()
    frame = MyFrame()
    app.MainLoop()