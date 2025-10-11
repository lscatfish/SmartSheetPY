import asyncio
import threading

import wx
from wx import Panel, stc
from wx.stc import StyledTextCtrl
from ..tools.funcs_StyledTextCtrl import _setSpec, _AddMessage, _ClearText
from ..tools.funcs_Gauge import _CtrlProgress
from SSPY.communitor.sharedvalue import SharedInt


class BaseFrame(wx.Frame):
    """为了多态"""

    def __init__(self, parent, title, size):
        super().__init__(parent, title = title, size = size)
        self.__font_size = 12
        self.font_default = wx.Font(
            self.__font_size,  # 字号（点/磅）
            wx.FONTFAMILY_DEFAULT,
            wx.FONTSTYLE_NORMAL,
            wx.FONTWEIGHT_NORMAL)
        """默认字体"""
        self.main_panel = wx.Panel(self)  # 创建主画布
        """主画布"""

        self.msg_panel_default = wx.Panel(self.main_panel)  # 创建默认消息画布
        """默认消息画布"""
        self.msg_text_default = self.CreateStyledTextCtrl(
            self.msg_panel_default,
            self.font_default
        )
        """定义一个msg_text用于容纳消息，标准消息器"""
        msg_sizer = wx.BoxSizer(wx.VERTICAL)
        msg_sizer.Add(self.msg_text_default, 1, wx.EXPAND | wx.ALL, 10)
        self.msg_panel_default.SetSizer(msg_sizer)
        self.msg_text_default.SetEditable(False)

        self.progress_panel_default = wx.Panel(self.main_panel)
        """进度条画布"""
        self.progress_gauge_default_using = False
        """默认进度条是否被占用"""
        self.progress_gauge_default = (
            wx.Gauge(self.progress_panel_default, range = 100, size = (-1, 25)))
        """默认进度条"""
        self.progress_percent_default = wx.StaticText(self.progress_panel_default, label = "0.00%")
        """进度条进度值"""
        self.progress_prompt_default = wx.StaticText(self.progress_panel_default, label = "已就绪！！")
        """进度条提示"""
        self.progress_percent_default.SetFont(self.font_default)
        self.progress_prompt_default.SetFont(self.font_default)
        progress_sizer = wx.BoxSizer(wx.HORIZONTAL)
        progress_sizer.Add(
            self.progress_gauge_default, 1,
            flag = wx.ALIGN_CENTER_VERTICAL | wx.RIGHT | wx.BOTTOM | wx.LEFT,
            border = 20)
        progress_sizer.Add(
            self.progress_percent_default, 0,
            flag = wx.ALIGN_LEFT,
            border = 5)
        progress_sizer.Add(
            self.progress_prompt_default, 0,
            flag = wx.ALIGN_LEFT | wx.LEFT | wx.BOTTOM | wx.RIGHT,
            border = 10)
        self.progress_panel_default.SetSizer(progress_sizer)

        # 线程列
        self.thread_list: list[threading.Thread] = []

    def AddMessage(self, msg, color = 'default', ptime = True):
        """
        标准消息，可重写的方法
        Args:
            color 可选：'default' | 'red' | 'green'  （想加颜色再扩字典即可）
        """
        if isinstance(self.msg_text_default, StyledTextCtrl):
            wx.CallAfter(_AddMessage(self.msg_text_default, msg, color, ptime))
        pass

    def ClearText(self, event):
        """清除默认StyledTextCtrl中的内容，可以重写"""
        wx.CallAfter(_ClearText, self.msg_text_default)
        pass

    def response_children(self, request: str | tuple | list):
        """应答子线程"""
        pass

    def register(self):
        """注册器，注册各个模块必要的模块"""
        pass


    def CreateStyledTextCtrl(
        self,
        parent_msg_panel: Panel,
        font,
        style = wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL | wx.VSCROLL,
        ScrollWidth: int = 5000,
        ScrollWidthTracking: bool = True,
        font_styleNum = stc.STC_STYLE_DEFAULT,
        style_spec_default = True
    ):
        """
        自parent_msg_panel创建一个StyledTextCtrl
        Args:
            parent_msg_panel:父panel，是一个
            style: default : wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL | wx.VSCROLL
            ScrollWidth:横向滚动条宽度
            ScrollWidthTracking:横向滚动条追踪
            font_styleNum:字体设置
            font:字体设置
            style_spec_default:是否启用默认颜色系统
        Returns:
            返回一个StyledTextCtrl
        """
        mt = stc.StyledTextCtrl(parent_msg_panel, style = style)
        mt.SetScrollWidth(ScrollWidth)
        mt.SetScrollWidthTracking(ScrollWidthTracking)
        mt.StyleSetFont(font_styleNum, font)
        mt.SetMarginWidth(1, 0)  # 隐藏行号区
        if style_spec_default:
            _setSpec(mt)
        return mt

    @property
    def font_size(self):
        """字体大小"""
        return self.__font_size

    @font_size.setter
    def font_size(self, value):
        """字体大小"""
        if isinstance(value, int) and value > 0:
            self.__font_size = value

    def progress_default_reset(self):
        """重置进度条"""

        def __reset_progress_gauge_default_using():
            self.progress_gauge_default_using = False

        def __reset_progress_prompt_default():
            self.progress_prompt_default = '已就绪！！'

        wx.CallAfter(self.progress_gauge_default.SetValue, 0)
        wx.CallAfter(self.progress_percent_default.SetLabelText, '0.00%')
        wx.CallAfter(__reset_progress_gauge_default_using)
        wx.CallAfter(__reset_progress_prompt_default)

    def progress_default_start(self):
        """开始进度条"""

        def __set_progress_gauge_default_using():
            self.progress_gauge_default_using = True

        def __set_progress_prompt_default():
            self.progress_prompt_default = '工作中...'

        wx.CallAfter(__set_progress_gauge_default_using)
        wx.CallAfter(__set_progress_prompt_default)
        wx.CallAfter(self.progress_gauge_default.SetValue, 0)
        wx.CallAfter(self.progress_percent_default.SetLabelText, '0.00%')

    def progress_default_control(self, shared_int: SharedInt):
        """
        默认进度条的控制函数
        Args:
            shared_int:共享变量
        """
        wx.CallAfter(self.progress_default_start)
        while True:
            """每100ms检测一次"""
            i1 = shared_int.int1
            i2 = shared_int.int2
            wx.CallAfter(
                _CtrlProgress,
                self.progress_gauge_default,
                i1, i2,
                self.progress_prompt_default)
            if i2 == 0 or i1 >= i2:
                break
            asyncio.sleep(0.05)
        wx.CallAfter(self.progress_default_reset)
