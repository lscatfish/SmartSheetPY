# msg_hub.py
import wx
from queue import Queue
import threading

_q = Queue()

def init_msg_hub(text_ctrl):
    """
    在主线程初始化时调用一次，把 wx 控件注册进来
    """
    # def _poll():
    #     while True:
    #         item = _q.get()          # (text, color)
    #         if item is None: break   # 退出哨兵
    #         text, color = item
    #         text_ctrl.AppendText(text + '\n')
    #         if color:
    #             # 简单染色示例：最后一行染 color
    #             line = text_ctrl.GetLineCount() - 2
    #             text_ctrl.StartStyling(text_ctrl.PositionFromLine(line))
    #             text_ctrl.SetStyling(len(text), color2style(color))
    #         text_ctrl.ScrollToLine(text_ctrl.GetLineCount())

    # 启动一个 wx 定时器，常驻主线程轮询队列
    timer = wx.Timer()
    timer.Bind(wx.EVT_TIMER, lambda e: _drain())
    timer.Start(50)   # 20 次/秒，足够流畅

    def _drain():
        while not _q.empty():
            item = _q.get_nowait()
            if item is None: break
            text, color = item
            text_ctrl.AppendText(text + '\n')
            if color:
                line = text_ctrl.GetLineCount() - 2
                text_ctrl.StartStyling(text_ctrl.PositionFromLine(line))
                text_ctrl.SetStyling(len(text), color2style(color))
            text_ctrl.ScrollToLine(text_ctrl.GetLineCount())

def color2style(c):
    return {'red': 1, 'green': 2}.get(c, 0)

# 唯一入口：任何地方直接发消息
def post(msg, color=None):
    """
    线程安全，可在任意线程/模块调用
    """
    _q.put((msg, color))