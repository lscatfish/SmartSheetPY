"""针对进度条的操做"""
import wx
from SSPY.communitor.sharedvalue import SharedInt


def _SetProgress(gauge_obj: wx.Gauge, sh: SharedInt):
    """
    int1表示当前的处理数量，int2表示总的处理数量
    Args:
        gauge_obj:进度条对象
        sh:共享变量
    """
    if sh.int2 == 0:
        gauge_obj.SetValue(100)
    rg = abs(int(100 * float(sh.int1) / float(sh.int2)))
    gauge_obj.SetValue(rg)
