import sys
import threading
import logging
from types import FrameType
from typing import Callable, Any, Optional, List
import functools

logging.basicConfig(level = logging.WARNING)
_local = threading.local()


def _get_trace_stack() -> List[Callable]:
    if not hasattr(_local, 'trace_stack'):
        _local.trace_stack = []
    return _local.trace_stack


def _push_trace(trace_func: Callable):
    stack = _get_trace_stack()
    stack.append(trace_func)
    sys.settrace(trace_func)


def _pop_trace():
    stack = _get_trace_stack()
    stack.pop()
    sys.settrace(stack[-1] if stack else None)


class _STOP:
    __slots__ = ()


STOP = _STOP()


class _FuncTracer:
    __slots__ = ("cond", "varnames", "active", "owner_func_name", "retval", "trigger_frame", "owner_class")

    def __init__(self, cond: Callable, varnames: List[str], retval: Any):
        self.cond = cond
        self.varnames = varnames
        self.active = False
        self.owner_func_name: Optional[str] = None
        self.owner_class: Optional[type] = None  # 记录方法所属的类
        self.retval = retval
        self.trigger_frame: Optional[FrameType] = None  # 保存触发条件时的帧

    def _eval_one(self, frame: FrameType, name: str) -> Any:
        if not isinstance(name, str):
            return name
        try:
            # 1. 优先检查局部变量（f_locals）
            if name in frame.f_locals:
                return frame.f_locals[name]

            # 2. 检查闭包变量（针对嵌套函数中的自由变量，如self）
            # 闭包变量名列表（co_freevars）
            free_vars = frame.f_code.co_freevars
            if name in free_vars:
                # 闭包单元格对象（__closure__是单元格列表）
                closure = frame.f_locals.get('__closure__') or ()
                # 找到变量对应的单元格索引
                idx = free_vars.index(name)
                if idx < len(closure):
                    # 从单元格中获取变量值
                    return closure[idx].cell_contents

            # 3. 检查全局变量（f_globals）
            if name in frame.f_globals:
                return frame.f_globals[name]

            # 4. 处理属性链（如self.__stopFlag）
            if "." in name:
                parts = name.split(".")
                obj = self._eval_one(frame, parts[0])  # 递归解析基础对象（如self）

                # 验证基础对象不是字符串（避免之前的错误）
                if isinstance(obj, str) and parts[0] == "self":
                    raise TypeError(f"self 被错误解析为字符串，无法访问属性 {parts[1]}")

                for attr in parts[1:]:
                    # 处理私有变量修饰（__xxx -> _类名__xxx）
                    if attr.startswith("__") and not attr.endswith("__"):
                        cls = obj.__class__
                        mangled_attr = f"_{cls.__name__}{attr}"
                        attr = mangled_attr

                    obj = getattr(obj, attr)
                return obj

            return name
        except Exception as e:
            logging.warning(f"解析变量 {name} 失败: {e}")
            # 此处不回退为字符串，避免后续错误扩散（可根据需要调整）
            return name  # 或者返回一个特殊标记，如None

    def _check(self, frame: FrameType) -> bool:
        values = [self._eval_one(frame, v) for v in self.varnames]
        try:
            return bool(self.cond(*values))
        except Exception:
            return False

    def _make_return(self) -> Any:
        """使用触发条件时的帧解析返回值"""
        if self.retval is None:
            return None
        if not isinstance(self.retval, str):
            return self.retval
        # 若未触发条件（正常返回），直接返回retval字面量
        if self.trigger_frame is None:
            return self.retval
        # 解析返回值（使用触发时的帧）
        val = self._eval_one(self.trigger_frame, self.retval)
        # 特殊处理STOP哨兵
        return STOP if val == "STOP" else val

    def _trace(self, frame: FrameType, event: str, arg: Any) -> Optional[Callable]:
        if frame.f_code.co_name != self.owner_func_name:
            return None  # 仅监控目标函数

        # 记录方法所属的类（从frame的局部变量self中获取）
        if event == "call" and self.owner_class is None:
            try:
                self.owner_class = frame.f_locals["self"].__class__
            except (KeyError, AttributeError):
                pass  # 非实例方法可能没有self，不强制

        if event == "call":
            self.active = True
            self.trigger_frame = None  # 重置触发帧
            # 函数调用时立即检测（第一行执行前）
            if self._check(frame):
                self.trigger_frame = frame  # 保存触发帧
                raise StopIteration("Variable condition met")
            return self._trace
        if event == "return":
            self.active = False
            return self._trace
        if event == "line" and self.active and self._check(frame):
            self.trigger_frame = frame  # 保存触发帧
            raise StopIteration("Variable condition met")
        return self._trace


def monitor_variables(varnames: list[str],
                      condition: Callable[..., bool],
                      retval: Any = None):
    def decorator(func: Callable) -> Callable:
        tracer = _FuncTracer(condition, varnames, retval)
        tracer.owner_func_name = func.__name__

        @functools.wraps(func)
        def wrapper(*args, **kw):
            _push_trace(tracer._trace)
            try:
                res = func(*args, **kw)
                return tracer._make_return() if res is STOP else res
            except StopIteration as e:
                if str(e) == "Variable condition met":
                    return tracer._make_return()
                raise
            finally:
                _pop_trace()

        return wrapper

    return decorator
