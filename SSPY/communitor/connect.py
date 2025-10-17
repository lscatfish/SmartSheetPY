"""链接器与解除链接器"""
import time

from .core import get_response

def connect_progress_default(in_list: list[str] | None):
    """
    链接到默认进度条
    Args:
        in_list:要链接到进度条的对象
    """
    if not (isinstance(in_list, list) and len(in_list) > 0): return None
    while True:
        response, shared_int = get_response(('request_progress_gauge_default', len(in_list)))
        if response == 'wait':
            if isinstance(shared_int, int):
                time.sleep(abs(shared_int))
        elif response == 'done':
            return 'done'
        else:
            raise ValueError(f'main thread response error : response = {response}')

def post_progress_default(now_idx, max_idx, prompt=''):
    """
    发布当前的进度条信息
    Args:
        now_idx:当前的值
        max_idx:最大值
        prompt:提示词
    """
    get_response(('progress_gauge_default_now', now_idx, max_idx, prompt))

def disconnect_progress_default():
    """
    取消进度条的链接
    """
    get_response('close_progress_gauge_default')
