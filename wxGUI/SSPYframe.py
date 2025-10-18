# -*- coding: utf-8 -*-
"""
修正方法
wxPython 用于控制SSPY模块的的窗口
"""
import threading
import wx
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
        self.btn_stop = None
        """中止"""
        self.btn_clear = None
        """清屏"""
        self.btn3 = None
        """青字班报名"""
        self.btn2 = None
        """生成汇总表"""
        self.btn1 = None
        """生成签到表"""
        self.btn_prompt = None
        """提示"""
        self.__thread_stop_flag_qc = threading.Event()
        self.__thread_stop_flag_qc.set()
        """监控qc的终止工具"""
        self.__font_size = 12
        """全局字体大小"""
        self.SetDPIHigh()  # 设置高DPI
        super().__init__(parent, title = title, size = (1300, 900))

        self.RegisterTextHub(self.AddMessage)  # 注册消息站
        self.InitUI()  # 初始化UI构架
        self.DisableButtons()
        self.Center()
        self.Show()

        wx.CallAfter(self.AddMessage, '加载配置文件中...')  # 害怕加载未成功，用原来的函数
        self.__qc = QC

        # 大文件加载
        wx.CallAfter(self.__background_load)

    def InitUI(self):
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # 1. 上方按钮区
        btn_panel = wx.Panel(self.main_panel)
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.btn_prompt = wx.Button(btn_panel, label = '提示')
        self.btn1 = wx.Button(btn_panel, label = "功能1：生成签到表")
        self.btn2 = wx.Button(btn_panel, label = "功能2：生成汇总表")
        self.btn3 = wx.Button(btn_panel, label = "功能3：青字班报名")
        self.btn_stop = wx.Button(btn_panel, label = "中止")
        self.btn_clear = wx.Button(btn_panel, label = "清屏")

        for btn in (self.btn_prompt, self.btn1, self.btn2, self.btn3, self.btn_stop, self.btn_clear):
            btn.SetFont(self.font_default)
            btn_sizer.Add(btn, 1, wx.ALL | wx.CENTER, 15)
        btn_panel.SetSizer(btn_sizer)
        main_sizer.Add(btn_panel, 0, wx.EXPAND | wx.TOP | wx.BOTTOM, 15)

        # 2. 下方滚动消息区（StyledTextCtrl）
        main_sizer.Add(self.msg_panel_default, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        # 3. 按钮事件
        self.btn_prompt.Bind(wx.EVT_BUTTON, lambda event: self.on_prompt(event))
        self.btn1.Bind(wx.EVT_BUTTON, lambda e: self.StartTask(1))
        self.btn2.Bind(wx.EVT_BUTTON, lambda e: self.StartTask(2))
        self.btn3.Bind(wx.EVT_BUTTON, lambda e: self.StartTask(3))
        self.btn_stop.Bind(wx.EVT_BUTTON, lambda e: self.on_interrupt())
        self.btn_clear.Bind(wx.EVT_BUTTON, lambda e: self.ClearText())
        # self.Bind(wx.EVT_CLOSE,self.on_exit)
        # 最好采用默认关闭方式

        main_sizer.Add(self.progress_panel_default, 0, wx.EXPAND | wx.TOP | wx.BOTTOM, 5)

        self.main_panel.SetSizer(main_sizer)
        self.Center()
        return

    def __background_load(self):
        """后台慢慢 import + 初始化，界面不卡"""
        wx.Yield()

        def __worker():
            # ===== 重定向 stdout / stderr =====
            # 让第三方库的 print 也进窗口
            self.ReregisterSysOut()
            # 劫持 Windows C 运行时 stderr，使其输出重定向到 wx 消息窗口
            self.ReregisterCOut()

            import SSPY.hijack.hijack_paddlex
            a = SSPY.hijack.hijack_paddlex

            # 注册子线程交流器
            self.RegisterResponseCommunitor(self.response_children)
            # 注册SSPY的交流器
            self.RegisterSSPYCommunitor()

            from wxGUI.communitor.text_hub import postText
            postText('配置文件加载成功！！！')

            from SSPY.globalconstants import GlobalConstants as gc
            gc.create_folders_must()

            wx.CallAfter(self.EnableButtons)

        threading.Thread(target = __worker, daemon = True).start()

    def DisableButtons(self):
        for btn in (self.btn_prompt, self.btn1, self.btn2, self.btn3):
            btn.Disable()

    def EnableButtons(self):
        for btn in (self.btn_prompt, self.btn1, self.btn2, self.btn3):
            btn.Enable()

    def BackgroundTask(self, task_type):
        pompt = f"开始执行功能{task_type}，按钮已锁定..." \
            if self.msg_text_default.GetLength() == 0 \
            else f"\n\n开始执行功能{task_type}，按钮已锁定..."
        self.AddMessage(pompt, ptime = False)
        try:
            self.__thread_stop_flag_qc.clear()
            self.__qc.start(task_type, self.__thread_stop_flag_qc)
            wx.CallAfter(
                self.AddMessage,
                ptime = False,
                msg = f'# -------------------------- 功能 {task_type} 结束 -------------------------- #\n\n',
                color = 'green')
        finally:
            wx.CallAfter(self.EnableButtons)
            wx.CallAfter(self.__thread_stop_flag_qc.set)
            self.__qc.reset()
            self.progress_default_reset()

    def StartTask(self, task_type):
        self.DisableButtons()
        # 启动后台
        threading.Thread(target = self.BackgroundTask, args = (task_type,), daemon = True).start()

    def on_interrupt(self):
        """终止青字班的功能"""
        if not self.__thread_stop_flag_qc.is_set():
            postText("正在中止功能执行......", color = 'red', ptime = False)
            self.__thread_stop_flag_qc.set()
        else:
            postText("没有正在执行的功能！！！", color = 'red', ptime = False)

    def on_prompt(self, _):
        """提示"""
        from SSPY.globalconstants import GlobalConstants
        if self.msg_text_default.GetLength() > 0:
            postText('\n\n', ptime = False)
        postText(msg = '# -------------------------------------- 提示 -------------------------------------- #\n',
            color = 'green', ptime = False)

        postText(msg = '请保证同源文件 "output/" 已备份，任何功能的运行都可能覆盖 "output/" 中的文件！！！\n',
            color = 'red', ptime = False)

        postText(msg = '* 功能1与功能2的输入文件的文件名应按照以下规则：', color = 'green', ptime = False)
        postText(msg = '  ① 文件名必须至少含有青字班班名的关键字（如：“青科班”的xlsx文件必须含有“科”字）',
            color = 'green', ptime = False)
        postText(msg = '  ② 文件名不能含多于一个关键字（如：“青科班的志向”这个文件名包含了“科”“志”两个关键字',
            color = 'green', ptime = False)
        postText(msg = f'  ③ 这些关键字包含：{[c[0] for c in GlobalConstants.cns]}\n',
            color = 'green', ptime = False)

        postText(msg = '* 功能 1', color = 'green', ptime = False)
        postText(msg = '  ① 青字班的花名册请放置在与程序同源的文件夹 "input/all/" 中',
            color = 'green', ptime = False)
        postText(msg = '  ② 班委提供的集中授课报名表请放置在与程序同源的文件夹 "input/app/" 中',
            color = 'green', ptime = False)
        postText(msg = '  ③ 如果要生成所有人的花名册，请将花名册复制一份放置在文件夹 "input/app/" 中',
            color = 'green', ptime = False)
        postText(msg = '  ④ 如果输出了未知人员，请修改花名册中的信息，让未知人员不再输出！！！\n',
            color = 'green', ptime = False)

        postText(msg = '* 功能 2', color = 'green', ptime = False)
        postText(msg = '  ① 青字班的花名册请放置在与程序同源的文件夹 "input/all/" 中',
            color = 'green', ptime = False)
        postText(msg = '  ② 请确保与程序同源的文件夹文件 "storage/storage.xlsx" 存在',
            color = 'green', ptime = False)
        postText(msg = '  ③ 请确保签到照片的命名含有关键词且不多于一个',
            color = 'green', ptime = False)
        postText(msg = '  ④ 如果一个班的照片有多个，可以使用在照片最后加上数字的方式来区分',
            color = 'green', ptime = False)
        postText(msg = '  ⑤ 第一次运行功能2的时候会下载接近1.2GB的大模型文件，此过程需要联网',
            color = 'green', ptime = False)
        postText(msg = '  ⑥ 功能2运行所需时间有点长，请耐心等待\n', color = 'green', ptime = False)

        postText(msg = '* 功能 3', color = 'green', ptime = False)
        postText(msg = '  ① 请将解压之后的文件直接放置在文件放置在 "input/sign_for_QingziClass/" 中',
            color = 'green', ptime = False)
        postText(msg = '  ② 无法解析的文报名表会输出到 "output/sign_for_QingziClass_out/unknown/" 中，请一定前去查看！\n',
            color = 'green', ptime = False)

        postText('# -------------------------------------- 提示 -------------------------------------- #', 'green', False)


    def on_exit(self, _):
        import sys
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        del self.__qc
        self.Destroy()

    def response_children(self, request: str | tuple | list):
        """回复子线程，注册为_main_process_func，此函数在主线程中运行"""
        if isinstance(request, str):
            return self.rsp_str(request)
        elif isinstance(request, tuple):
            return self.rsp_tuple(request)
        return 'exit-error'

    def rsp_str(self, request: str):
        match request:
            case 'close_progress_gauge_default':
                self.progress_default_reset()  # 重置进度条
        return 'exit-error'

    def rsp_tuple(self, request: tuple):
        match len(request):
            case 2:
                return self.rsp_tuple2(request)
            case 4:
                return self.rsp_tuple4(request)
            case _:
                return 'exit-error'

    def rsp_tuple2(self, request: tuple):
        match request[0]:
            case 'ppocr_model_dir_unexist':
                return self.handle_model_unexist(request[1])
            case 'request_progress_gauge_default':
                """请求一个进度条"""
                return self.handle_start_progress(request)
            case _:
                return 'exit-error'

    def rsp_tuple4(self, request: tuple):
        match request[0]:
            case 'msg':
                return self.handle_postText(request)
            case 'progress_gauge_default_now':
                self.progress_default_set(request[1], request[2], request[3])
                return ''
            case _:
                return 'exit-error'

    def handle_model_unexist(self, unexist: list):
        """处理模型不存在的问题"""
        # 等待用户选择
        l = len(unexist)
        if l == 0:
            return 'exit-error'
        m = '以下模型不存在：\n'
        for un in unexist:
            m += (un + '\n')
        m += ('下载需要 ' + str(l * 110) + 'MB\n')
        m += '是否下载？'
        r = wx.MessageBox(m, '信息', wx.OK | wx.ICON_INFORMATION | wx.CANCEL)
        match r:
            case wx.OK:
                return 'continue'
            case wx.CANCEL:
                self.on_interrupt()
                postText('# -------------------------- 退出功能2 -------------------------- #',
                    'red', False)
                return 'exit'
            case _:
                self.on_interrupt()
                postText('# -------------------------- 退出功能2 -------------------------- #',
                    'red', False)
                return 'exit'

    def handle_postText(self, request: tuple):
        """处理发送消息的问题"""
        postText(request[1], color = request[2], ptime = request[3])
        return None

    def handle_start_progress(self, request: tuple):
        """请求一个进度条"""
        if self.progress_gauge_default_using:
            return 'wait', 3  # 暂停3s
        self.progress_default_start()
        return 'done', ''
