import wx
import time
import random


class MyFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title = "文件处理进度示例", size = (600, 400))

        # 创建主面板
        self.main_panel = wx.Panel(self)
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.main_panel.SetSizer(self.main_sizer)

        # 添加一些控制按钮和文件信息显示
        self.setup_controls()

        # 添加弹性空间，将进度条部分推到底部
        self.main_sizer.AddStretchSpacer(prop = 1)

        # 设置底部进度条区域
        self.setup_progress_section()

        # 创建定时器
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.update_progress, self.timer)

        # 初始化任务状态变量
        self.current_progress = 0
        self.total_files = 0
        self.processed_files = 0
        self.is_paused = False
        self.current_file = ""

        self.Centre()
        self.Show()

    def setup_controls(self):
        """设置上部控制区域"""
        # 文件数量选择控件
        file_sizer = wx.BoxSizer(wx.HORIZONTAL)
        file_label = wx.StaticText(self.main_panel, label = "模拟文件数量:")
        self.file_choice = wx.Choice(self.main_panel, choices = ['10', '50', '100', '200'])
        self.file_choice.SetSelection(0)  # 默认选择10个文件
        file_sizer.Add(file_label, 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 5)
        file_sizer.Add(self.file_choice, 1, wx.EXPAND)

        # 按钮控件
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.start_btn = wx.Button(self.main_panel, label = "开始处理")
        self.pause_btn = wx.Button(self.main_panel, label = "暂停")
        self.reset_btn = wx.Button(self.main_panel, label = "重置")

        self.pause_btn.Disable()  # 初始时暂停按钮不可用

        button_sizer.Add(self.start_btn, 1, wx.EXPAND | wx.RIGHT, 5)
        button_sizer.Add(self.pause_btn, 1, wx.EXPAND | wx.RIGHT, 5)
        button_sizer.Add(self.reset_btn, 1, wx.EXPAND)

        # 当前文件处理信息显示
        self.current_file_label = wx.StaticText(self.main_panel, label = "当前文件: 无")
        self.file_info_label = wx.StaticText(self.main_panel, label = "已处理: 0/0 文件")

        # 绑定按钮事件
        self.start_btn.Bind(wx.EVT_BUTTON, self.on_start_task)
        self.pause_btn.Bind(wx.EVT_BUTTON, self.on_pause_task)
        self.reset_btn.Bind(wx.EVT_BUTTON, self.on_reset_task)

        # 添加到主sizer
        self.main_sizer.Add(file_sizer, 0, wx.EXPAND | wx.ALL, 10)
        self.main_sizer.Add(button_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        self.main_sizer.Add(self.current_file_label, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        self.main_sizer.Add(self.file_info_label, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

    def setup_progress_section(self):
        """设置底部进度条区域"""
        self.bottom_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # 创建进度条，范围设为100表示百分比
        self.progress_gauge = wx.Gauge(self.main_panel, range = 100, size = (-1, 20), style = wx.GA_HORIZONTAL)

        # 创建进度百分比文本
        self.progress_text = wx.StaticText(self.main_panel, label = "0%")

        # 创建状态文本
        self.status_text = wx.StaticText(self.main_panel, label = "准备就绪", style = wx.ALIGN_LEFT)

        # 将控件添加到水平sizer
        self.bottom_sizer.Add(self.progress_gauge, 1, flag = wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, border = 5)
        self.bottom_sizer.Add(self.progress_text, 0, flag = wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, border = 10)
        self.bottom_sizer.Add(self.status_text, 0, flag = wx.ALIGN_CENTER_VERTICAL)

        # 将水平sizer添加到主sizer
        self.main_sizer.Add(self.bottom_sizer, 0, flag = wx.EXPAND | wx.ALL, border = 10)

    def on_start_task(self, event):
        """开始处理任务"""
        if self.current_progress >= 100:  # 如果任务已完成，先重置
            self.on_reset_task(None)

        # 获取选择的文件数量
        self.total_files = int(self.file_choice.GetString(self.file_choice.GetSelection()))
        self.processed_files = 0

        # 更新按钮状态
        self.start_btn.Disable()
        self.pause_btn.Enable()
        self.reset_btn.Enable()

        # 更新状态信息
        self.status_text.SetLabelText("文件处理中...")
        self.file_info_label.SetLabelText(f"已处理: {self.processed_files}/{self.total_files} 文件")

        # 启动定时器，每100毫秒更新一次
        self.timer.Start(100)

    def on_pause_task(self, event):
        """暂停/继续任务"""
        if self.is_paused:
            # 继续任务
            self.timer.Start(100)
            self.pause_btn.SetLabel("暂停")
            self.status_text.SetLabelText("文件处理中...")
            self.is_paused = False
        else:
            # 暂停任务
            self.timer.Stop()
            self.pause_btn.SetLabel("继续")
            self.status_text.SetLabelText("已暂停")
            self.is_paused = True

    def on_reset_task(self, event):
        """重置任务"""
        self.timer.Stop()
        self.current_progress = 0
        self.processed_files = 0
        self.total_files = 0
        self.is_paused = False

        # 重置UI状态
        self.progress_gauge.SetValue(0)
        self.progress_text.SetLabelText("0%")
        self.status_text.SetLabelText("准备就绪")
        self.current_file_label.SetLabelText("当前文件: 无")
        self.file_info_label.SetLabelText("已处理: 0/0 文件")

        # 重置按钮状态
        self.start_btn.Enable()
        self.pause_btn.Disable()
        self.pause_btn.SetLabel("暂停")

    def update_progress(self, event):
        """定时器事件，更新进度条和状态文本"""
        # 模拟文件处理 - 每次增加随机进度
        increment = random.randint(1, 5)
        self.current_progress += increment

        # 确保进度不超过100%
        if self.current_progress > 100:
            self.current_progress = 100

        # 更新进度条和百分比文本
        self.progress_gauge.SetValue(self.current_progress)
        self.progress_text.SetLabelText(f"{self.current_progress}%")

        # 模拟文件处理完成
        if self.current_progress >= 100:
            self.processed_files += 1
            self.current_progress = 0

            # 更新文件信息
            self.file_info_label.SetLabelText(f"已处理: {self.processed_files}/{self.total_files} 文件")

            # 模拟下一个文件
            if self.processed_files < self.total_files:
                file_number = self.processed_files + 1
                self.current_file_label.SetLabelText(f"当前文件: 示例文件_{file_number}.txt")
                self.status_text.SetLabelText(f"处理文件 {file_number}/{self.total_files}")
            else:
                # 所有文件处理完成
                self.timer.Stop()
                self.status_text.SetLabelText("所有文件处理完成！")
                self.current_file_label.SetLabelText("当前文件: 无")

                # 更新按钮状态
                self.start_btn.Enable()
                self.pause_btn.Disable()
                self.reset_btn.Enable()


if __name__ == "__main__":
    app = wx.App()
    frame = MyFrame()
    app.MainLoop()
