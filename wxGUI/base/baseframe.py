import threading

import wx
from wx import Panel, stc
from wx.stc import StyledTextCtrl

from ..hijack.hijack_sysstd import WxTextCtrlStdout
from ..tools.funcs_StyledTextCtrl import _setSpec, _AddMessage, _ClearText


class BaseFrame(wx.Frame):
    """为了多态!!!"""

    def __init__(
        self,
        parent,
        title,
        size,
        init_msg_text = True,
        init_progress = True, ):
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

        if init_msg_text:
            self.msg_panel_default = wx.Panel(self.main_panel)  # 创建默认消息画布
            """默认消息画布"""
            self.msg_text_default = self.CreateStyledTextCtrl(
                self.msg_panel_default,
                self.font_default)
            self.msg_text_default.Bind(wx.EVT_MOUSEWHEEL, self.OnMouseWheel)
            """定义一个msg_text用于容纳消息，标准消息器"""
            msg_sizer = wx.BoxSizer(wx.VERTICAL)
            msg_sizer.Add(self.msg_text_default, 1, wx.EXPAND | wx.ALL, 10)
            self.msg_panel_default.SetSizer(msg_sizer)
            self.msg_text_default.SetEditable(False)

        if init_progress:
            self.progress_panel_default = wx.Panel(self.main_panel)
            """进度条画布"""
            progress_panel1 = wx.Panel(self.progress_panel_default)
            """上方画布"""
            # progress_panel2 = wx.Panel(self.progress_panel_default)
            # """下方的画布"""
            self.progress_gauge_default_using = False
            """默认进度条是否被占用"""
            self.progress_gauge_default = (
                wx.Gauge(progress_panel1, range = 100, size = (-1, 25)))
            """默认进度条"""
            self.progress_percent_default = wx.StaticText(progress_panel1, label = "0.00%")
            """进度条进度值"""
            self.progress_prompt_default = wx.StaticText(progress_panel1, label = "已就绪！！")
            """进度条提示"""
            self.progress_downp_default = wx.StaticText(self.progress_panel_default, label = "", size = (-1, 20))
            """下方解析提示"""
            self.progress_percent_default.SetFont(self.font_default)
            self.progress_prompt_default.SetFont(self.font_default)
            self.progress_downp_default.SetFont(
                wx.Font(10,
                    wx.FONTFAMILY_DEFAULT,
                    wx.FONTSTYLE_NORMAL,
                    wx.FONTWEIGHT_NORMAL))

            # 下方的全部布局
            progress_sizer1 = wx.BoxSizer(wx.HORIZONTAL)
            progress_sizer1.Add(
                self.progress_gauge_default, 1,
                flag = wx.ALIGN_CENTER_VERTICAL | wx.RIGHT | wx.LEFT,
                border = 20)
            progress_sizer1.Add(
                self.progress_percent_default, 0,
                flag = wx.ALIGN_LEFT | wx.RIGHT,
                border = 10)
            progress_sizer1.Add(
                self.progress_prompt_default, 0,
                flag = wx.ALIGN_LEFT | wx.LEFT | wx.RIGHT,
                border = 10)
            progress_panel1.SetSizer(progress_sizer1)
            progress_sizer2=wx.BoxSizer(wx.VERTICAL)
            progress_sizer2.Add(
                progress_panel1,
                flag = wx.EXPAND|wx.CENTER,
                border = 5)
            progress_sizer2.Add(
                self.progress_downp_default,
                flag = wx.ALIGN_LEFT | wx.LEFT | wx.RIGHT|wx.BOTTOM|wx.TOP,
                border = 20  )
            self.progress_panel_default.SetSizer(progress_sizer2)


        self.event_thread_interrupt = threading.Event()
        """停止线程的标志"""
        self.__interrupt_resource_recovery: dict = {}
        """线程紧急中断的回收机制"""

    def RecoveryInterruptResource(self):
        """回收中断之后的资源"""
        pass

    def AddMessage(self, msg, color = 'default', ptime = True):
        """
        标准消息，可重写的方法
        Args:
            color 可选：'default' | 'red' | 'green'  （想加颜色再扩字典即可）
        """
        if isinstance(self.msg_text_default, StyledTextCtrl):
            wx.CallAfter(_AddMessage, self.msg_text_default, msg, color, ptime)
        pass

    def ClearText(self, event = None):
        """清除默认StyledTextCtrl中的内容，可以重写"""
        wx.CallAfter(_ClearText, self.msg_text_default)
        pass

    def ChoosePath(self, TextCtrl_obj: wx.TextCtrl):
        """
        为一个TextCtrl添加路径选择
        Args:
            TextCtrl_obj:要修改的wx.TextCtrl对象
        """
        dlg = wx.DirDialog(
            self,
            message = "选择文件夹",
            defaultPath = TextCtrl_obj.GetValue(),  # 使用当前输入框的值作为默认路径
            style = wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST)
        if dlg.ShowModal() == wx.ID_OK:
            selected_path = dlg.GetPath()
            TextCtrl_obj.SetValue(selected_path)  # 将选择的路径设置到输入框
        dlg.Destroy()

    def OnMouseWheel(self, event):
        """控制鼠标滚轮的滑动"""
        if event.ShiftDown():
            # 横向滚动
            delta = -event.GetWheelRotation() // 60  # 正负方向
            current_x = self.msg_text_default.GetXOffset()
            new_x = max(0, current_x + delta * 20)  # 20 px/步
            self.msg_text_default.SetXOffset(new_x)
        else:
            event.Skip()  # 纵向交给原生

    def response_children(self, request: str | tuple | list):
        """应答子线程"""
        pass

    def register(self):
        """运行注册器，注册各个模块必要的模块"""
        pass

    def ReregisterSysOut(self):
        """===== 重定向 stdout / stderr ====="""
        # 让第三方库的 print 也进窗口
        import sys
        sys.stdout = WxTextCtrlStdout(self.msg_text_default)  # 普通信息
        sys.stderr = WxTextCtrlStdout(self.msg_text_default, 'red')  # 错误染红

    def ReregisterCOut(self):
        """重定向C的输出库"""
        # 劫持 Windows C 运行时 stderr，使其输出重定向到 wx 消息窗口
        import wxGUI.hijack.crt_redirect  # 只要 import 就自动完成重定向
        a = wxGUI.hijack.crt_redirect.a

    def RegisterTextHub(self, addmsg):
        """注册消息站"""
        from wxGUI.communitor.text_hub import register_text_hub
        register_text_hub(
            lambda msg, color = 'default', ptime = True:
            wx.CallAfter(addmsg, msg, color, ptime))

    def RegisterSSPYCommunitor(self):
        """注册SSPY对外的交流器，请在RegisterResponseCommunitor注册只后注册此程序"""
        from SSPY import register_SSPY_communitor
        from wxGUI.communitor.core import msg
        register_SSPY_communitor(msg)

    def RegisterResponseCommunitor(self, resp):
        """注册主线程回复函数"""
        # 注册并启动子线程交流器
        import wxGUI.communitor
        wxGUI.communitor.register_main_process(resp)

    def SetDPIHigh(self):
        """设置高DPI"""
        from wxGUI.DPIset import set_DPI
        set_DPI()

    def CreateStyledTextCtrl(
        self,
        parent_msg_panel: Panel,
        font,
        style = wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL | wx.VSCROLL,
        ScrollWidth: int = 5000,
        ScrollWidthTracking: bool = True,
        font_styleNum = stc.STC_STYLE_DEFAULT,
        style_spec_default = True):
        """
        自parent_msg_panel创建一个StyledTextCtrl
        Args:
            parent_msg_panel:父panel
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

    def CreatePathChooseFs(
        self,
        parent_msg_panel: Panel,
        font,
        TextCtrl_size = (800, 30),
        Button_size = (100, 30),
        Button_binder_auto = False,
        StaticText_prompt_lib: str = None):
        """
        创建一个路径选择器行
        Args:
            parent_msg_panel:父panel
            font:字体
            TextCtrl_size:可以控制的输入文字的size
            Button_size:按钮的大小
            Button_binder_auto:自动绑定按钮
            StaticText_prompt_lib:固定提示词
        """
        stp = None  # 提示
        if isinstance(StaticText_prompt_lib, str):
            stp = wx.StaticText(parent = parent_msg_panel, label = StaticText_prompt_lib)
            stp.SetFont(font)
        btn = wx.Button(parent = parent_msg_panel, label = '浏览...', size = Button_size)
        btn.SetFont(font)
        tc = wx.TextCtrl(parent_msg_panel, size = TextCtrl_size)
        # tc.SetFont(font)
        if Button_binder_auto:
            btn.Bind(wx.EVT_BUTTON, lambda event: self.ChoosePath(tc))
        return stp, tc, btn  # 返回提示，选择框，选择按钮

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

        wx.CallAfter(self.progress_gauge_default.SetValue, 0)
        wx.CallAfter(self.progress_percent_default.SetLabelText, '0.00%')
        wx.CallAfter(__reset_progress_gauge_default_using)
        wx.CallAfter(self.progress_prompt_default.SetLabelText, '已就绪！！')
        wx.CallAfter(self.progress_downp_default.SetLabelText, '')

    def progress_default_start(self):
        """开始进度条"""

        def __set_progress_gauge_default_using():
            self.progress_gauge_default_using = True

        wx.CallAfter(__set_progress_gauge_default_using)
        wx.CallAfter(self.progress_prompt_default.SetLabelText, '工作中...')
        wx.CallAfter(self.progress_gauge_default.SetValue, 0)
        wx.CallAfter(self.progress_percent_default.SetLabelText, '0.00%')
        wx.CallAfter(self.progress_downp_default.SetLabelText, '')

    def progress_default_set(self, int1, int2, prompt):
        """
        设置进度条的量
        Args:
            int1:当前值
            int2:总的值
            prompt:提示词
        """
        if int2 == 0:
            self.progress_gauge_default.SetValue(100)
            self.progress_percent_default.SetLabelText("100.00%")
            self.progress_downp_default.SetLabelText(prompt)
        rg = abs(100 * float(int1) / float(int2))
        self.progress_gauge_default.SetValue(int(rg))
        self.progress_percent_default.SetLabelText(f"{rg:.2f}%")
        self.progress_downp_default.SetLabelText(prompt)
