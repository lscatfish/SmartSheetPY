"""为程序设置DPI感知"""


def set_DPI():
    """设置高dpi参数"""
    import ctypes
    from .communitor.text_hub import postText
    try:
        # 设置应用程序为DPI感知
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception as e:
        postText("设置DPI感知失败")
