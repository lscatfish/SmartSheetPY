# -*- coding: utf-8 -*-
"""
修正方法
wxPython 用于控制SSPY模块的的窗口
"""
import sys
import threading
import wx
import wx.stc as stc  # 关键控件
from wxGUI.hijack.hijack_sysstd import WxTextCtrlStdout
from wxGUI.communitor.text_hub import postText
from wxGUI.base.baseframe import BaseFrame


class SSPYMainFrame(BaseFrame):
    """修正过后的主框架"""

    def __init__(self, parent, title, QC):
        """
        Args:
            parent:父框架
            title:标题
            QC:青字班控制类
        """
        self.msg_text = None
        self.btn_stop = None
        self.btn_clear = None
        self.btn3 = None
        self.btn2 = None
        self.btn1 = None

        self.__thread_stop_flag_qc = threading.Event()
        """监控qc的终止工具"""
        self.__thread_wait_response_children = threading.Event()
        """阻塞回复函数等待用户输入的工具"""

        self.__font_size = 12  # 全局字体大小
        super().__init__(parent, title = title, size = (1000, 650))

        # 1. 先注册消息站
        from wxGUI.communitor.text_hub import register_text_hub
        register_text_hub(
            lambda msg, color = 'default', ptime = True:
            wx.CallAfter(self.AddMessage, msg, color, ptime))
        from wxGUI.DPIset import set_DPI
        set_DPI()

        self.InitUI()
        self.DisableButtons()
        self.Show()

        wx.CallAfter(self.AddMessage, '加载配置文件中...')
        self.__qc = QC

        # 大文件加载
        wx.CallAfter(self.__background_load)


    def InitUI(self):
        main_panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # 1. 上方按钮区
        btn_panel = wx.Panel(main_panel)
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.btn1 = wx.Button(btn_panel, label = "功能1：生成签到表")
        self.btn2 = wx.Button(btn_panel, label = "功能2：生成汇总表")
        self.btn3 = wx.Button(btn_panel, label = "功能3：青字班报名")
        self.btn_stop = wx.Button(btn_panel, label = "中止")
        self.btn_clear = wx.Button(btn_panel, label = "清屏")
        font = wx.Font(
            self.__font_size,  # 字号（点/磅）
            wx.FONTFAMILY_DEFAULT,
            wx.FONTSTYLE_NORMAL,
            wx.FONTWEIGHT_NORMAL)

        for btn in (self.btn1, self.btn2, self.btn3, self.btn_stop, self.btn_clear):
            btn.SetFont(font)
            btn_sizer.Add(btn, 1, wx.ALL | wx.CENTER, 15)
        btn_panel.SetSizer(btn_sizer)
        main_sizer.Add(btn_panel, 0, wx.EXPAND | wx.TOP | wx.BOTTOM, 15)

        # 2. 下方滚动消息区（StyledTextCtrl）
        main_sizer.Add(self.msg_panel_default, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        # 3. 按钮事件
        self.btn1.Bind(wx.EVT_BUTTON, lambda e: self.StartTask(1))
        self.btn2.Bind(wx.EVT_BUTTON, lambda e: self.StartTask(2))
        self.btn3.Bind(wx.EVT_BUTTON, lambda e: self.StartTask(3))
        self.btn_stop.Bind(wx.EVT_BUTTON, lambda e: self.StopQCTask())
        self.btn_clear.Bind(wx.EVT_BUTTON, lambda e: self.ClearText())
        # self.Bind(wx.EVT_CLOSE,self.on_exit)
        # 最好采用默认关闭方式

        main_panel.SetSizer(main_sizer)
        self.Center()
        return

    def __background_load(self):
        """后台慢慢 import + 初始化，界面不卡"""
        wx.Yield()

        def __worker():
            # ===== 重定向 stdout / stderr =====
            # 让第三方库的 print 也进窗口
            sys.stdout = WxTextCtrlStdout(self.msg_text)  # 普通信息
            sys.stderr = WxTextCtrlStdout(self.msg_text, 'red')  # 错误染红

            # 劫持 Windows C 运行时 stderr，使其输出重定向到 wx 消息窗口
            import wxGUI.hijack.crt_redirect  # 只要 import 就自动完成重定向
            a = wxGUI.hijack.crt_redirect.a

            from wxGUI.communitor.text_hub import postText
            import SSPY.hijack.hijack_paddlex
            a = SSPY.hijack.hijack_paddlex

            # 注册子线程交流器
            import wxGUI.communitor
            wxGUI.communitor.register_main_process(self.response_children)

            # 注册SSPY的交流器
            from SSPY import register_SSPY_communitor
            register_SSPY_communitor(wxGUI.communitor.core.msg)

            postText('配置文件加载成功！！！')

            from SSPY.globalconstants import GlobalConstants as gc
            gc.create_folders_must()

            wx.CallAfter(self.EnableButtons)

        threading.Thread(target = __worker, daemon = True).start()

    def DisableButtons(self):
        for btn in (self.btn1, self.btn2, self.btn3):
            btn.Disable()

    def EnableButtons(self):
        for btn in (self.btn1, self.btn2, self.btn3):
            btn.Enable()

    def BackgroundTask(self, task_type):
        pompt = f"开始执行功能{task_type}，按钮已锁定..." \
            if self.msg_text.GetLength() == 0 \
            else f"\n\n开始执行功能{task_type}，按钮已锁定..."
        self.AddMessage(pompt, ptime = False)
        try:
            self.__thread_stop_flag_qc.clear()
            self.__qc.start(task_type, self.__thread_stop_flag_qc)
            self.__qc.reset()
            wx.CallAfter(
                self.AddMessage,
                ptime = False,
                msg = f'# -------------------------- 功能 {task_type} 结束 -------------------------- #\n\n',
                color = 'green')
        finally:
            wx.CallAfter(self.EnableButtons)

    def StartTask(self, task_type):
        self.DisableButtons()
        # 启动后台
        threading.Thread(target = self.BackgroundTask, args = (task_type,), daemon = True).start()

    def StopQCTask(self):
        """终止青字班的功能"""
        if not self.__thread_stop_flag_qc.is_set():
            postText("正在中止功能执行......", color = 'red', ptime = False)
            self.__thread_stop_flag_qc.set()
        else:
            postText("没有正在执行的功能！！！", color = 'red', ptime = False)

    def response_children(self, request: str | tuple | list):
        """回复子线程，注册为_main_process_func，此函数在主线程中运行"""
        if isinstance(request, str):
            pass
        elif isinstance(request, tuple):
            if request[0] == 'ppocr_model_dir_unexist':
                if isinstance(request[1], list) and len(request[1]) > 0:
                    # 等待用户选择
                    m = '以下模型不存在：\n'
                    for i in request[1]:
                        m += (i + '\n')
                    m += ('下载需要 ' + str(len(request[1]) * 110) + 'MB\n')
                    m += '是否下载？'
                    r = wx.MessageBox(m, '信息', wx.OK | wx.ICON_INFORMATION | wx.CANCEL)
                    match r:
                        case wx.OK:
                            return 'continue'
                        case wx.CANCEL:
                            self.StopQCTask()
                            postText('# -------------------------- 退出功能2 -------------------------- #', 'red', False)
                            return 'exit'
                        case _:
                            return 'exit-error'
                    # self.__thread_wait_response_children.wait()
            if request[0] == 'msg':
                if len(request) == 4:
                    postText(request[1], color = request[2], ptime = request[3])
                    return None
        return 'exit-error'


    def on_exit(self, _):
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        del self.__qc
        self.Destroy()
