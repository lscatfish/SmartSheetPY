# -*- coding: utf-8 -*-
"""
向外部线程发送消息的函数
"""
_response_fun = None
"""答复过程函数"""


def register_communitor(fun):
    """注册交换器"""
    global _response_fun
    _response_fun = fun


def get_response(request):
    """发送请求，获取回复"""
    if _response_fun is None:
        import warnings
        warnings.warn('SSPY.communitor的线程信息交换函数未初始化', RuntimeWarning)
        return None
    return _response_fun(request)


def postText(msg: str, color: str = 'default', ptime = True):
    """只单纯发送消息，不请求"""
    import warnings
    if _response_fun is None:
        warnings.warn('SSPY.communitor的线程信息交换函数未初始化', RuntimeWarning)
        return None
    elif isinstance(color, str) and isinstance(msg, str) and isinstance(ptime, bool):
        return _response_fun(('msg', msg, color, ptime))
    else:
        warnings.warn('SSPY的消息发送函数postText必须按照 (str,str,bool) 的格式', RuntimeWarning)
    return None

def mprint(msg: str, color: str = 'default', ptime = False):
    """标准输出函数"""
    """适配wxGUI"""
    global _response_fun
    if _response_fun is None:
        match color:
            case 'default':print(msg)
            case 'red':print(f"\033[31m{msg}\033[0m")
            case 'green':print(f"\033[32m{msg}\033[0m")
            case 'yellow':print(f"\033[33m{msg}\033[0m")
            case _: print(msg)
        return
    else:
        postText(msg, color, ptime)