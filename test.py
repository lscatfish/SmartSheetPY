import sys
import threading
from types import FrameType
from typing import Callable, Any, Optional, List
import functools


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
    __slots__ = ("cond", "varnames", "active", "owner_func_name", "retval")

    def __init__(self, cond: Callable, varnames: List[str], retval: Any):
        self.cond = cond
        self.varnames = varnames
        self.active = False
        self.owner_func_name: Optional[str] = None
        self.retval = retval

    # ---------- 统一解析 ----------
    def _eval_one(self, frame: FrameType, name: str) -> Any:
        if not isinstance(name, str):
            return name
        try:
            # 1. 局部
            if name in frame.f_locals:
                return frame.f_locals[name]
            # 2. 全局
            if name in frame.f_globals:
                return frame.f_globals[name]
            # 3. 属性链（含 name-mangling）
            if "." in name:
                part0, *parts = name.split(".")
                obj = frame.f_locals[part0]
                for attr in parts:
                    if attr.startswith("__") and not attr.endswith("__"):
                        attr = f"_{obj.__class__.__name__}{attr}"
                    obj = getattr(obj, attr)
                return obj
            # 4. 找不到 → 回退成字面量（字符串本身）
            return name
        except Exception:
            # 解析失败也回退成字面量
            return name

    # ---------- 检查 ----------
    def _check(self, frame: FrameType) -> bool:
        values = [self._eval_one(frame, v) for v in self.varnames]
        try:
            return bool(self.cond(*values))
        except Exception:
            return False

    # ---------- 返回值 ----------
    def _make_return(self, frame: FrameType):
        if self.retval is None:
            return None
        if not isinstance(self.retval, str):
            return self.retval
        return self._eval_one(frame, self.retval)

    # ---------- trace ----------
    def _trace(self, frame: FrameType, event: str, arg: Any) -> Optional[Callable]:
        if frame.f_code.co_name != self.owner_func_name:
            return None
        if event == "call":
            self.active = True
            return self._trace
        if event == "return":
            self.active = False
            return self._trace
        if event == "line" and self.active and self._check(frame):
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
                return tracer._make_return(sys._getframe(0).f_back) if res is STOP else res
            except StopIteration as e:
                if str(e) == "Variable condition met":
                    return tracer._make_return(sys._getframe(0).f_back)
                raise
            finally:
                _pop_trace()

        return wrapper

    return decorator


# -------------------------------------------------
# 示例
# -------------------------------------------------
G = 100


class Foo:
    cls_var = 0

    def __init__(self):
        self.__priv = 10
        self.default = "default_value"

    @monitor_variables(["self.__priv", "Foo.cls_var"],
        lambda priv, cls: priv <= 5 or cls >= 3,
        retval = "self.default")
    def work1(self):
        for i in range(10):
            self.__priv -= 1
            Foo.cls_var += 1
            print(i, self.__priv, Foo.cls_var)
        return "done"

    @monitor_variables(["self.__priv"], lambda priv: priv == 7, retval = [])
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


# 递归：返回 STOP 哨兵
@monitor_variables(["n"], lambda n: n == 5, retval = "STOP")
def rec(n):
    print("rec", n)
    if n == 0:
        return 0
    nxt = rec(n - 1)
    return nxt if nxt is STOP else 1 + nxt


if __name__ == "__main__":
    f = Foo()
    print("work1 ->", f.work1())
    print("work2 ->", f.work2())
    print("work3 ->", f.work3())
    print("rec   ->", rec(10))
