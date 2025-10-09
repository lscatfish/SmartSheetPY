import wx
from wx import Panel, stc
from wx.stc import StyledTextCtrl
from ..tools.funcs import _setSpec, _AddMessage


class BaseFrame(wx.Frame):
    """为了多态"""

    def __init__(self, parent, title, size):
        super().__init__(parent, title, size = size)
        self.__font_size = 12
        self.font_default = wx.Font(
            self.__font_size,  # 字号（点/磅）
            wx.FONTFAMILY_DEFAULT,
            wx.FONTSTYLE_NORMAL,
            wx.FONTWEIGHT_NORMAL)
        self.main_panel = wx.Panel(self)  # 创建主画布
        self.msg_panel_default = wx.Panel(self.main_panel)  # 创建默认消息画布
        self.msg_text_default = self.CreateStyledTextCtrl(self.msg_panel_default)  # 定义一个msg_text用于容纳消息，标准消息器

    def AddMessage(self, msg, color = 'default', ptime = True):
        """
        标准消息，可重写的方法
        Args:
            color 可选：'default' | 'red' | 'green'  （想加颜色再扩字典即可）
        """
        if isinstance(self.msg_text_default, StyledTextCtrl):
            wx.CallAfter(_AddMessage(self.msg_text_default, msg, color, ptime))
        pass

    @staticmethod
    def CreateStyledTextCtrl(
        parent_msg_panel: Panel,
        style = wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL | wx.VSCROLL,
        ScrollWidth: int = 5000,
        ScrollWidthTracking: bool = True,
        font_styleNum = stc.STC_STYLE_DEFAULT,
        font = wx.Font(
            12,  # 字号（点/磅）
            wx.FONTFAMILY_DEFAULT,
            wx.FONTSTYLE_NORMAL,
            wx.FONTWEIGHT_NORMAL),
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
