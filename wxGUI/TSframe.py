"""搜索器的界面"""
import os
import threading
import wx

from .base.baseframe import BaseFrame
from wxGUI.communitor.text_hub import postText


class TSMainFrame(BaseFrame):
    def __init__(self, parent, title):
        """
        Args:
            parent (wx.Frame):父框架
            title:标题
        """
        from .DPIset import set_DPI
        set_DPI()

        super().__init__(parent = parent, title = title, size = (1000, 650))

        self.target_path = ''  # 目标路径
        self.target_text = ''  # 目标文字
        self.main_stop_event = threading.Event()  # 主暂停器

        main_sizer = wx.BoxSizer(wx.VERTICAL)  # 主结构

        # 上方按钮区域
        btn_panel = wx.Panel(self.main_panel)  # 按钮画布
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)  # 按钮区域
        self.btn_find = wx.Button(btn_panel, label = '查找')
        self.btn_save = wx.Button(btn_panel, label = '保存结果')
        self.btn_stop = wx.Button(btn_panel, label = '中止')
        self.btn_clear = wx.Button(btn_panel, label = '清屏')
        self.btn_find.Bind(wx.EVT_BUTTON, self.on_find)
        self.btn_clear.Bind(wx.EVT_BUTTON, self.ClearText)
        for btn in (self.btn_find, self.btn_save, self.btn_stop, self.btn_clear):
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
        self.target_text_text = wx.TextCtrl(target_panel_1, pos = (10, 10), size = (600, 30))
        self.target_path_text = wx.TextCtrl(target_panel_2, pos = (10, 10), size = (600, 30))
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
        self.main_panel.SetSizer(main_sizer)
        self.Center()
        self.Show()


    def on_select(self, event):
        # 创建文件夹选择对话框
        dlg = wx.DirDialog(
            self,
            message = "选择文件夹",
            defaultPath = self.target_path_text.GetValue(),  # 使用当前输入框的值作为默认路径
            style = wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST
        )

        if dlg.ShowModal() == wx.ID_OK:
            selected_path = dlg.GetPath()
            self.target_path_text.SetValue(selected_path)  # 将选择的路径设置到输入框
        dlg.Destroy()

    def on_find(self, event):
        self.DisableButtons()
        self.target_path_text.SetEditable(False)
        self.target_text_text.SetEditable(False)

        self.target_path = self.target_path_text.GetValue()
        self.target_text = self.target_text_text.GetValue()
        if self.target_path == '':
            postText('请输入路径！！！', 'red')
        elif not os.path.exists(self.target_path):
            postText('选择的路径不存在！！！', 'red')

        self.target_path_text.SetEditable(True)
        self.target_text_text.SetEditable(True)
        self.EnableButtons()

    def DisableButtons(self):
        """禁用部分按钮"""
        for b in (self.btn_save, self.btn_find, self.btn_clear, self.btn_select):
            wx.CallAfter(b.Disable)
        pass

    def EnableButtons(self):
        """启用部分按钮"""
        for b in (self.btn_save, self.btn_find, self.btn_clear, self.btn_select):
            wx.CallAfter(b.Enable)
        pass
