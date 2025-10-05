"""
向外部线程发送消息的函数
"""
_process_fun = None
"""过程函数"""


def register_communitor(fun):
    """注册交换器"""
    global _process_fun
    _process_fun = fun


def get_response(request):
    if _process_fun is None:
            import warnings
            warnings.warn('SSPY.communitor的线程信息交换函数未初始化', RuntimeWarning)
            return None
    return _process_fun(request)

