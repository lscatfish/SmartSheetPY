# -*- coding: utf-8 -*-

_appender = None  # 全局变量：存 (窗口对象, 方法)

def register_text_hub(appender_fn):
    """
    注册text发布站
    appender_fn 必须是线程安全的函数，比如：
    lambda msg,color=None: wx.CallAfter(frame.AddMessage, msg, color)
    """
    global _appender
    _appender = appender_fn


def postText(msg, color = 'default', ptime = True):
    """任意线程/模块直接调用，发布消息"""
    if _appender is None:
        import warnings
        warnings.warn('msg_hub 未初始化', RuntimeWarning)
        return
    _appender(msg, color, ptime)


