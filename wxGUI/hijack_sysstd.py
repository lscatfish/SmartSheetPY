"""此项目用于劫持标准库的io功能"""

import wx


class WxTextCtrlStdout:
    """
    把 stdout/err 重定向到 wx.stc.StyledTextCtrl（或 TextCtrl）
    内部用 wx.CallAfter 保证线程安全
    """

    def __init__(self, text_ctrl, color = None):
        self.text_ctrl = text_ctrl
        self.color = color  # 可为 None / 'red' / 'green' ...

    def write(self, string):
        if string and string != '\n':  # 过滤空行
            wx.CallAfter(self._append, string)

    def _append(self, string):
        # 如果前面你已经实现了 AddMessage，直接复用即可
        # 这里演示最简：直接插尾
        tc = self.text_ctrl
        tc.AppendText(string)
        # 追底
        tc.ScrollToLine(tc.GetLineCount())

    def flush(self): pass  # print 需要这个接口
