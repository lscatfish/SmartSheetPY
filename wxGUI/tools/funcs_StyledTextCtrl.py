import wx
import time
from wx.stc import StyledTextCtrl

color2style = {'red': 1, 'green': 2, 'yellow': 3, 'default': 0}
style2spec = {0: 'fore:#000000', 1: 'fore:#DC143C,bold', 2: 'fore:#2E8B57', 3: "fore:#FFFF00,bold"}


def _setSpec(text_obj: StyledTextCtrl):
    """设置默认颜色列表，请加入到主线程队列"""
    for key in style2spec:
        text_obj.StyleSetSpec(styleNum = key, spec = style2spec[key])


def _AddMessage(text_obj: StyledTextCtrl, msg, color = 'default', ptime = True):
    """
    请加入到主线程队列
    color 可选：'default' | 'red' | 'green'  （想加颜色再扩字典即可）
    """
    editable = text_obj.IsEditable()
    if not editable:
        text_obj.SetEditable(True)
    current_time = time.strftime("[%H:%M:%S]", time.localtime())
    full_msg = f"{current_time} {msg}\n" if ptime else f"{msg}\n"

    # === 1. 追加 ===
    start_pos = text_obj.GetLength()  # 插入前末尾
    text_obj.AppendText(full_msg)
    end_pos = text_obj.GetLength()  # 插入后末尾

    # === 2. 染色（精确区间）===
    style_id = color2style.get(color, 0)
    text_obj.StartStyling(start_pos)  # 从插入点开始
    text_obj.SetStyling(end_pos - start_pos, style_id)

    # === 3. 追底 ===
    text_obj.ScrollToLine(text_obj.GetLineCount())

    if not editable:
        text_obj.SetEditable(False)


def _ClearText(text_obj: StyledTextCtrl):
    """请加入到主线程队列"""
    editable = text_obj.IsEditable()
    if not editable:
        text_obj.SetEditable(True)
    text_obj.ClearAll()
    if not editable:
        text_obj.SetEditable(False)
