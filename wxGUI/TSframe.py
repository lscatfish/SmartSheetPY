"""搜索器的界面"""
import os
import sys
import threading
import wx

from .base.baseframe import BaseFrame
from wxGUI.communitor.text_hub import postText
from .hijack.hijack_sysstd import WxTextCtrlStdout


class TSMainFrame(BaseFrame):
    def __init__(self, parent, title):
        """
        Args:
            parent (wx.Frame):父框架
            title:标题
        """
        from .DPIset import set_DPI
        set_DPI()

        super().__init__(parent = parent, title = title, size = (1500, 900))

        self.target_path = ''
        """目标路径"""
        self.target_text = ''
        """目标文字"""
        self.main_stop_event = threading.Event()  # 主暂停器

        main_sizer = wx.BoxSizer(wx.VERTICAL)  # 主结构

        # 上方按钮区域
        btn_panel = wx.Panel(self.main_panel)  # 按钮画布
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)  # 按钮区域
        self.btn_load = wx.Button(btn_panel, label = '加载')
        self.btn_find = wx.Button(btn_panel, label = '查找')
        self.btn_save = wx.Button(btn_panel, label = '保存结果')
        self.btn_interrupt = wx.Button(btn_panel, label = '中止')
        self.btn_clear = wx.Button(btn_panel, label = '清屏')
        self.btn_load.Bind(wx.EVT_BUTTON, self.on_load)
        self.btn_find.Bind(wx.EVT_BUTTON, self.on_find)
        self.btn_clear.Bind(wx.EVT_BUTTON, self.ClearText)
        self.btn_interrupt.Bind(wx.EVT_BUTTON, self.on_interrupt)
        for btn in (self.btn_load, self.btn_find, self.btn_save, self.btn_interrupt, self.btn_clear):
            btn.SetFont(self.font_default)
            btn_sizer.Add(btn, 1, wx.ALL | wx.CENTER, 10)
        btn_panel.SetSizer(btn_sizer)

        # 中间的目标和文件夹区域
        target_panel = wx.Panel(self.main_panel)
        target_panel_1 = wx.Panel(target_panel)  # 一级子画布，用于添加提示
        target_panel_2 = wx.Panel(target_panel)  # 一级子画布，用于添加提示
        target_sizer = wx.BoxSizer(wx.VERTICAL)
        target_sizer_1 = wx.BoxSizer(wx.HORIZONTAL)
        target_sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
        st1 = wx.StaticText(target_panel_1, label = "搜索目标:", pos = (10, 10))
        st2 = wx.StaticText(target_panel_2, label = "搜索路径:", pos = (10, 10))
        st1.SetFont(self.font_default)
        st2.SetFont(self.font_default)
        self.target_text_text = wx.TextCtrl(target_panel_1, pos = (10, 10), size = (800, 30))
        """搜索的文字"""
        self.target_path_text = wx.TextCtrl(target_panel_2, pos = (10, 10), size = (800, 30))
        """目标路径"""
        self.btn_select = wx.Button(target_panel_2, label = "浏览...", pos = (10, 10), size = (100, 30))
        self.btn_select.Bind(wx.EVT_BUTTON, self.on_select)
        self.btn_select.SetFont(self.font_default)
        for f in (st1, self.target_text_text):
            target_sizer_1.Add(f, 0, wx.ALL | wx.CENTER | wx.EXPAND, 5)
        for f in (st2, self.target_path_text, self.btn_select):
            target_sizer_2.Add(f, 0, wx.ALL | wx.CENTER | wx.EXPAND, 5)
        target_panel_1.SetSizer(target_sizer_1)
        target_panel_2.SetSizer(target_sizer_2)
        for f in (target_panel_1, target_panel_2):
            target_sizer.Add(f, 0, wx.ALL | wx.CENTER | wx.EXPAND, 5)
        target_panel.SetSizer(target_sizer)

        for f in (btn_panel, target_panel):
            main_sizer.Add(f, 0, wx.ALL | wx.CENTER | wx.EXPAND, 5)
        main_sizer.Add(self.msg_panel_default, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        main_sizer.Add(self.progress_panel_default, 0, wx.EXPAND | wx.RIGHT, 5)
        main_sizer.Add(self.progress_downp_default, 0, wx.ALIGN_LEFT | wx.LEFT | wx.BOTTOM, 20)
        self.main_panel.SetSizer(main_sizer)
        self.register()  # 注册
        self.Center()
        self.Show()

        from ToolSearching.core import SearchingTool
        self.__searching_tool = SearchingTool()  # 示例
        self.__if_preload = False  # 是否被预加载了
        self.btn_find.Disable()

    def unload(self):
        """子任务，解除加载"""
        # threading.Thread(target = self.__searching_tool.clear, daemon = True).start()
        wx.CallAfter(self.__searching_tool.clear)
        wx.CallAfter(self.btn_select.Enable)
        wx.CallAfter(self.btn_load.SetLabelText, '加载')
        wx.CallAfter(self.target_path_text.SetEditable, True)
        wx.CallAfter(self.btn_find.Disable)
        wx.CallAfter(self.progress_default_reset)
        self.__if_preload = False

    def on_load(self, event):
        """加载文件中的文件"""
        self.event_thread_interrupt.clear()
        self.DisableButtons()
        if self.__if_preload:  # 已经加载成功了，解除加载
            self.unload()
            self.EnableButtons()

        else:  # 没有加载，加载
            self.target_path = self.target_path_text.GetValue()
            if self.target_path == '':
                postText('请输入路径！！！', 'red', False)
                self.EnableButtons()
                return
            elif not os.path.exists(self.target_path):
                postText(f'{self.target_path} 不存在', 'red', False)
                self.EnableButtons()
                return

            wx.CallAfter(self.btn_load.SetLabelText, '解除')
            wx.CallAfter(self.btn_select.Disable)  # 禁用浏览文件夹
            wx.CallAfter(self.target_path_text.SetEditable, False)  # 禁用编辑路径
            self.__if_preload = True

            t = threading.Thread(
                target = self.TaskLoad,
                daemon = True)
            t.start()
            # 主线程禁止join

    def TaskLoad(self):
        """预加载工作"""
        self.__searching_tool.start(
            root_dir = self.target_path,
            stop_flag = self.event_thread_interrupt)
        if self.event_thread_interrupt.is_set():  # 退出方法
            wx.CallAfter(self.unload)
            postText('中断成功！！！\n\n', 'green', False)
            self.event_thread_interrupt.clear()
        else:
            wx.CallAfter(self.btn_find.Enable)
        wx.CallAfter(self.EnableButtons)

    def on_find(self, event):
        self.DisableButtons()
        self.target_text_text.SetEditable(False)
        self.target_text = self.target_text_text.GetValue()
        self.ClearText(None)
        wx.CallAfter(self.TaskFind)
        self.target_text_text.SetEditable(True)
        self.EnableButtons()

    def TaskFind(self):
        """运行搜索任务"""
        rst: list[tuple] = []
        if self.target_text == '':
            postText('请输入搜索值！！！\n\n', 'red', False)
            return
        self.__searching_tool.find(self.target_text, rst)
        if len(rst) == 0:
            postText(f'搜索目标“{self.target_text}”未找到\n\n', 'yellow', False)
            return
        for line in rst:
            postText(line[0] + '   ' + line[1], ptime = False)

    def on_select(self, event):
        dlg = wx.DirDialog(
            self,
            message = "选择文件夹",
            defaultPath = self.target_path_text.GetValue(),  # 使用当前输入框的值作为默认路径
            style = wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST)

        if dlg.ShowModal() == wx.ID_OK:
            selected_path = dlg.GetPath()
            self.target_path_text.SetValue(selected_path)  # 将选择的路径设置到输入框
            # threading.Thread(target = self.__searching_tool.clear, daemon = True).start()
            self.__if_preload = False
        dlg.Destroy()

    def on_interrupt(self, event):
        """中断函数"""
        self.event_thread_interrupt.set()


    def DisableButtons(self):
        """禁用部分按钮"""
        for b in (self.btn_load, self.btn_save, self.btn_clear):
            wx.CallAfter(b.Disable)

    def EnableButtons(self):
        """启用部分按钮"""
        for b in (self.btn_load, self.btn_save, self.btn_clear):
            wx.CallAfter(b.Enable)

    def response_children(self, request: str | tuple | list):
        """回复子线程，ATT：此函在主函数运行"""
        if isinstance(request, str):
            return self.rsp_str(request)
        elif isinstance(request, tuple):
            return self.rsp_tuple(request)
        return "exit-error"

    def register(self):
        """注册必要函数"""
        from .communitor.text_hub import register_text_hub
        register_text_hub(
            lambda msg, color = None, ptime = True:
            wx.CallAfter(self.AddMessage, msg, color, ptime))

        # ===== 重定向 stdout / stderr =====
        # 让第三方库的 print 也进窗口
        sys.stdout = WxTextCtrlStdout(self.msg_text_default)  # 普通信息
        sys.stderr = WxTextCtrlStdout(self.msg_text_default, 'red')  # 错误染红

        # 劫持 Windows C 运行时 stderr，使其输出重定向到 wx 消息窗口
        import wxGUI.hijack.crt_redirect  # 只要 import 就自动完成重定向
        a = wxGUI.hijack.crt_redirect.a

        from .communitor.core import register_main_process
        register_main_process(self.response_children)

        from SSPY import register_SSPY_communitor
        register_SSPY_communitor(wxGUI.communitor.msg)

    def rsp_str(self, request: str):
        """回复函数的str类型"""
        if request == 'close_progress_gauge':
            self.progress_gauge_default_using = False
            self.progress_default_reset()
            return ''
        return 'exit-error'

    def rsp_tuple(self, request: tuple):
        """回复tuple类型"""
        match len(request):
            case 2:
                return self.rsp_tuple2(request)
            case 3:
                return self.rsp_tuple3(request)
            case 4:
                return self.rsp_tuple4(request)
            case _:
                return 'exit-error'

    def rsp_tuple2(self, request: tuple):
        if request[0] == 'request_progress_gauge':
            """请求一个进度条过程"""
            if self.progress_gauge_default_using:  # 线程不安全
                """只有没有被使用的进度条可以被使用"""
                return 'wait', 3  # 回复等待3秒
            self.progress_default_start()
            return 'done', ''
        return 'exit-error'

    def rsp_tuple3(self, request: tuple):
        return 'exit-error'

    def rsp_tuple4(self, request: tuple):
        if request[0] == 'msg':
            postText(msg = request[1], color = request[2], ptime = request[3])
            return ''
        elif request[0] == 'progress_now':
            self.progress_default_set(request[1], request[2], request[3])
            return 'done'
        return 'exit-error'
