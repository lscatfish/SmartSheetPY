import queue
import wx

# 全局队列和状态（同之前的msg_comm.py）
_request_queue: queue.Queue[tuple[int, list[str]|str|tuple|dict]] = queue.Queue()
_response_queues: dict[int, queue.Queue] = {}
_request_id = 0
_main_process_func = None
"""需要注册"""


def _get_next_request_id():
    global _request_id
    _request_id += 1
    return _request_id


def _main_listener():
    while True:
        req_id, request = _request_queue.get()
        try:
            if _main_process_func is None:
                response = "错误：未注册主线程处理函数"
            else:
                if 'wx' in globals() and not wx.IsMainThread():
                    result_queue = queue.Queue()
                    wx.CallAfter(lambda: result_queue.put(_main_process_func(request)))
                    response = result_queue.get()
                else:
                    response = _main_process_func(request)
            _response_queues[req_id].put(response)
        finally:
            _request_queue.task_done()
            del _response_queues[req_id]


# 暴露给外部的API
def register_main_process(func):
    global _main_process_func
    _main_process_func = func


def msg(request):
    req_id = _get_next_request_id()
    reply_queue = queue.Queue()
    _response_queues[req_id] = reply_queue
    _request_queue.put((req_id, request))
    response = reply_queue.get()
    reply_queue.task_done()
    return response
