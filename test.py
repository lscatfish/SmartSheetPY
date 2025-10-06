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
    __slots__ = ("cond", "varnames", "active", "owner_func_name", "retval", "trigger_frame","owner_class")

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
            # 特殊处理self：必须从局部变量中获取实例，否则报错
            if name == "self":
                if "self" not in frame.f_locals:
                    raise ValueError(f"在方法 {self.owner_func_name} 的帧中未找到 self（可能帧错误）")
                return frame.f_locals["self"]  # 强制返回实例，不回退为字符串

            # 其他变量优先从局部/全局查找
            if name in frame.f_locals:
                return frame.f_locals[name]
            if name in frame.f_globals:
                return frame.f_globals[name]

            # 处理属性链（如self.__stopFlag）
            if "." in name:
                parts = name.split(".")
                obj = self._eval_one(frame, parts[0])  # 递归解析基础对象（如self）

                # 验证基础对象不是字符串（避免之前的错误）
                if isinstance(obj, str) and parts[0] == "self":
                    raise TypeError(f"self 被错误解析为字符串，无法访问属性 {parts[1]}")

                for attr in parts[1:]:
                    # 处理私有变量修饰（__xxx -> _类名__xxx）
                    if attr.startswith("__") and not attr.endswith("__"):
                        # 获取obj的实际类名（必须是实例的类，而非父类）
                        cls = obj.__class__
                        mangled_attr = f"_{cls.__name__}{attr}"
                        # 无需向上查找父类（私有变量仅属于定义它的类）
                        attr = mangled_attr

                    # 获取属性值
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


# 示例用法（不变）
G = 100


class Foo:
    cls_var = 0

    def __init__(self):
        self.__priv = 10
        self.default = "default_value"  # 期望返回的值

    @monitor_variables(["self.__priv", "Foo.cls_var"],
        lambda priv, cls: priv <= 5 or cls >= 3,
        retval = "self.default")  # 现在会正确解析
    def work1(self):
        for i in range(10):
            self.__priv -= 1
            Foo.cls_var += 1
            print(i, self.__priv, Foo.cls_var)
        return "done"

    @monitor_variables(["self.__priv"], lambda priv: priv == 7, retval = None)
    def work2(self):
        for i in range(10):
            self.__priv -= 1
            print(i, self.__priv)
        return "done"

    @monitor_variables(["self.__priv"], lambda priv: priv == 3, retval = "G")
    def work3(self):
        for i in range(10):
            self.__priv -= 1
            print(i, self.__priv)
        return "done"


@monitor_variables(["n"], lambda n: n == 5, retval = 3)  # 会返回STOP实例
def rec(n):
    print("rec", n)
    if n == 0:
        return 0
    q = rec(n - 1) + 1
    return q


if __name__ == "__main__":
    f = Foo()
    print("work1 ->", f.work1())
    print("work2 ->", f.work2())
    print("work3 ->", f.work3())
    print("rec   ->", rec(10))
