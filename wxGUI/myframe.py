#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
wxPython 演示：Shift+滚轮横向滚动文本内容（同步移动）
使用 wx.stc.StyledTextCtrl 替代 TextCtrl，以支持 SetXOffset
"""
import sys
import time
import threading
import wx
import wx.stc as stc  # 关键控件
from .hijack_sysstd import WxTextCtrlStdout


class MainFrame(wx.Frame):
    def __init__(self, parent, title, QC):
        """
        Args:
            parent:父框架
            title:标题
            QC:青字班控制类
        """
        self.__font_size = 12  # 全局字体大小
        super().__init__(parent, title = title, size = (800, 600))
        self.InitUI()
        self.DisableButtons()
        self.Show()

        # 1. 先注册消息站
        from .msg_hub import init_msg_hub, post
        init_msg_hub(lambda msg, color = None: wx.CallAfter(self.AddMessage, msg, color))
        post('加载配置文件中...')

        import wxGUI.crt_redirect  # 只要 import 就自动完成重定向
        a = wxGUI.crt_redirect.a

        # ===== 重定向 stdout / stderr =====
        # 让第三方库的 print 也进窗口
        sys.stdout = WxTextCtrlStdout(self.msg_text)  # 普通信息
        sys.stderr = WxTextCtrlStdout(self.msg_text, 'red')  # 错误染红

        self.__qc = QC

        # 大文件加载
        wx.CallAfter(self.__background_load)


    # -------------------- 后台加载 -------------------- #
    def __background_load(self):
        """后台慢慢 import + 初始化，界面不卡"""
        wx.Yield()

        def __worker():
            from .msg_hub import post
            import wxGUI.hijack_paddlex
            a = wxGUI.hijack_paddlex
            post('配置文件加载成功！！！')
            self.EnableButtons()

        threading.Thread(target = __worker, daemon = True).start()

    # -------------------- UI 构建 -------------------- #
    def InitUI(self):
        main_panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # 1. 上方按钮区
        btn_panel = wx.Panel(main_panel)
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.btn1 = wx.Button(btn_panel, label = "功能1：生成签到表")
        self.btn2 = wx.Button(btn_panel, label = "功能2：生成汇总表")
        self.btn3 = wx.Button(btn_panel, label = "功能3：青字班报名")
        font = wx.Font(
            self.__font_size,  # 字号（点/磅）
            wx.FONTFAMILY_DEFAULT,
            wx.FONTSTYLE_NORMAL,
            wx.FONTWEIGHT_NORMAL)

        for btn in (self.btn1, self.btn2, self.btn3):
            btn.SetFont(font)
            btn_sizer.Add(btn, 0, wx.ALL | wx.CENTER, 15)
        btn_panel.SetSizer(btn_sizer)
        main_sizer.Add(btn_panel, 0, wx.EXPAND | wx.TOP | wx.BOTTOM, 15)

        # 2. 下方滚动消息区（StyledTextCtrl）
        self.msg_panel = wx.Panel(main_panel)
        msg_sizer = wx.BoxSizer(wx.VERTICAL)

        self.msg_text = stc.StyledTextCtrl(
            self.msg_panel,
            style = wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL | wx.VSCROLL
        )
        # 让横向滚动条足够宽（字符像素单位）
        self.msg_text.SetScrollWidth(5000)
        self.msg_text.SetScrollWidthTracking(True)
        # 默认字体
        self.msg_text.StyleSetFont(
            stc.STC_STYLE_DEFAULT,
            wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        )

        self.msg_text.SetMarginWidth(1, 0)  # 隐藏行号区
        # 0 号样式=默认黑字
        self.msg_text.StyleSetSpec(0, "fore:#000000")  # 黑色
        # 1 号样式=红色警告
        self.msg_text.StyleSetSpec(1, "fore:#DC143C,bold")
        # 2 号样式=绿色成功
        self.msg_text.StyleSetSpec(2, "fore:#2E8B57")

        self.msg_text.StyleSetSize(stc.STC_STYLE_DEFAULT, self.__font_size)  # 像素
        # 让所有行继承默认大小
        self.msg_text.StyleClearAll()

        # 绑定滚轮
        self.msg_text.Bind(wx.EVT_MOUSEWHEEL, self.OnMouseWheel)

        msg_sizer.Add(self.msg_text, 1, wx.EXPAND | wx.ALL, 10)
        self.msg_panel.SetSizer(msg_sizer)
        main_sizer.Add(self.msg_panel, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        # 3. 按钮事件
        self.btn1.Bind(wx.EVT_BUTTON, lambda e: self.StartTask(1))
        self.btn2.Bind(wx.EVT_BUTTON, lambda e: self.StartTask(2))
        self.btn3.Bind(wx.EVT_BUTTON, lambda e: self.StartTask(3))

        main_panel.SetSizer(main_sizer)
        self.Center()

    # -------------------- 滚轮事件 -------------------- #
    def OnMouseWheel(self, event):
        if event.ShiftDown():
            # 横向滚动
            delta = -event.GetWheelRotation() // 60  # 正负方向
            current_x = self.msg_text.GetXOffset()
            new_x = max(0, current_x + delta * 20)  # 20 px/步
            self.msg_text.SetXOffset(new_x)
        else:
            event.Skip()  # 纵向交给原生

    # -------------------- 按钮锁/解锁 -------------------- #
    def DisableButtons(self):
        for btn in (self.btn1, self.btn2, self.btn3):
            btn.Disable()

    def EnableButtons(self):
        for btn in (self.btn1, self.btn2, self.btn3):
            btn.Enable()

    # -------------------- 追加消息 -------------------- #
    def AddMessage(self, msg, color = 'default'):
        """
        color 可选：'default' | 'red' | 'green'  （想加颜色再扩字典即可）
        """
        current_time = time.strftime("[%H:%M:%S]", time.localtime())
        # long_text = " ".join([f"测试文本{i}" for i in range(30)])
        full_msg = f"{current_time} {msg}\n"

        # 追底判断
        line_cnt = self.msg_text.GetLineCount()
        last_vis = self.msg_text.GetFirstVisibleLine() + self.msg_text.LinesOnScreen()
        should_scroll = last_vis >= line_cnt - 2

        # 追加到尾部（默认样式 0）
        self.msg_text.AppendText(full_msg)
        new_line = self.msg_text.GetLineCount() - 2  # 刚插入的那一行

        # 根据颜色参数染色
        color2style = {'red': 1, 'green': 2, 'default': 0}
        if color is None:
            self.SetMsgColor(new_line, 0)
        else:
            self.SetMsgColor(new_line, color2style.get(color, 0))

        if should_scroll:
            self.msg_text.ScrollToLine(self.msg_text.GetLineCount())

    # 新增一个给“整行”染色的辅助方法
    def SetMsgColor(self, line_no, style_no):
        """把第 line_no 行（0 起）全部字符设成 style_no 样式"""
        start = self.msg_text.PositionFromLine(line_no)
        end = self.msg_text.GetLineEndPosition(line_no)
        self.msg_text.StartStyling(start)
        self.msg_text.SetStyling(end - start, style_no)

    # -------------------- 后台任务 -------------------- #
    def BackgroundTask(self, task_type):
        try:
            self.__qc.start(task_type)
            self.__qc.reset()
            wx.CallAfter(self.AddMessage, '功能结束')
        finally:
            wx.CallAfter(self.EnableButtons)
            wx.CallAfter(self.AddMessage, "所有按钮已重新激活\n")

    # -------------------- 启动任务 -------------------- #
    def StartTask(self, task_type):
        self.DisableButtons()
        self.AddMessage(f"开始执行功能{task_type}，按钮已锁定...")
        threading.Thread(target = self.BackgroundTask, args = (task_type,), daemon = True).start()

    def on_exit(self):
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        self.Destroy()
