import wx


class PathDialog(wx.Dialog):
    """
# 示例使用方法
class MainFrame(wx.Frame):
    def __init__(self):
        super(MainFrame, self).__init__(
            None,
            title = "路径选择示例",
            size = (400, 200),
        )

        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        self.path_label = wx.StaticText(panel, label = "当前未选择路径")
        select_btn = wx.Button(panel, label = "打开路径选择对话框")

        vbox.Add(self.path_label, proportion = 0, flag = wx.ALL | wx.ALIGN_CENTER, border = 10)
        vbox.Add(select_btn, proportion = 0, flag = wx.ALL | wx.ALIGN_CENTER, border = 10)

        panel.SetSizer(vbox)

        select_btn.Bind(wx.EVT_BUTTON, self.on_open_dialog)

    def on_open_dialog(self, event):
        dialog = PathDialog(self)
        if dialog.ShowModal() == wx.ID_OK:
            selected_path = dialog.get_path()
            self.path_label.SetLabel(f"已选择路径: {selected_path}")
        dialog.Destroy()

if __name__ == "__main__":
    app = wx.App()
    frame = MainFrame()
    frame.Show()
    app.MainLoop()
    """

    def __init__(self, parent, title = "选择路径"):
        super(PathDialog, self).__init__(parent, title = title, size = (500, 150))

        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        # 第一行：路径输入框和选择按钮
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)

        wx.StaticText(panel, label = "路径:", pos = (15, 20))
        self.path_text = wx.TextCtrl(panel, pos = (10, 10), size = (450, 30))

        select_btn = wx.Button(panel, label = "浏览...", pos = (10, 10), size = (60, 30))
        select_btn.Bind(wx.EVT_BUTTON, self.on_select_path)

        hbox1.Add(self.path_text, proportion = 1, flag = wx.LEFT | wx.CENTER, border = 45)
        hbox1.Add(select_btn, proportion = 0, flag = wx.ALL, border = 5)

        # 第二行：确定和取消按钮
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)

        ok_btn = wx.Button(panel, label = "确定", size = (80, 30))
        cancel_btn = wx.Button(panel, label = "取消", size = (80, 30))

        hbox2.Add(ok_btn, flag = wx.RIGHT, border = 10)
        hbox2.Add(cancel_btn, flag = wx.LEFT, border = 10)

        # 组合布局
        vbox.Add(hbox1, proportion = 0, flag = wx.EXPAND | wx.ALL, border = 10)
        vbox.Add(hbox2, proportion = 0, flag = wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, border = 10)

        panel.SetSizer(vbox)

        # 绑定按钮事件
        ok_btn.Bind(wx.EVT_BUTTON, self.on_ok)
        cancel_btn.Bind(wx.EVT_BUTTON, self.on_cancel)

        self.selected_path = ""

    def on_select_path(self, event):
        # 创建文件夹选择对话框
        dlg = wx.DirDialog(
            self,
            message = "选择文件夹",
            defaultPath = self.path_text.GetValue(),  # 使用当前输入框的值作为默认路径
            style = wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST
        )

        if dlg.ShowModal() == wx.ID_OK:
            selected_path = dlg.GetPath()
            self.path_text.SetValue(selected_path)  # 将选择的路径设置到输入框

        dlg.Destroy()

    def on_ok(self, event):
        self.selected_path = self.path_text.GetValue()
        self.EndModal(wx.ID_OK)

    def on_cancel(self, event):
        self.EndModal(wx.ID_CANCEL)

    def get_path(self):
        return self.selected_path
