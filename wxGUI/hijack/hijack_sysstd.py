# -*- coding: utf-8 -*-
class WxTextCtrlStdout:
    def __init__(self, text_ctrl, color = None):
        self.text_ctrl = text_ctrl  # 其实就是 MainFrame.msg_text
        self.color = color

    def write(self, string):
        if string and string != '\n':
            from wxGUI.communitor.text_hub import postText  # 延迟导入避免循环
            postText(string.rstrip('\n'), self.color)  # 走现成的消息站

    def flush(self): pass
