"""针对进度条的操做"""
import wx


def _CtrlProgress(gauge_obj: wx.Gauge, int1, int2, text: wx.StaticText = None):
    """
    int1表示当前的处理数量，int2表示总的处理数量
    请使用CallAfter调用
    Args:
        gauge_obj:进度条对象
        text:提示文本
    """
    if int2 == 0:
        gauge_obj.SetValue(100)
        text.SetLabelText("100.00%")
    rg = abs(100 * float(int1) / float(int2))
    text.SetLabelText(f"{rg:.2f}%")
    gauge_obj.SetValue(int(rg))
