import wx


class WxTextCtrlStdout:
    def __init__(self, text_ctrl, color = None):
        self.text_ctrl = text_ctrl  # 其实就是 MainFrame.msg_text
        self.color = color

    def write(self, string):
        if string and string != '\n':
            from wxGUI.msg_hub import post  # 延迟导入避免循环
            post(string.rstrip('\n'), self.color)  # 走你现成的消息站

    def flush(self): pass
