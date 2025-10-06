import sys
import inspect
import functools
from types import FrameType
from typing import Callable, Any, Dict, Optional

STOP = object()  # 内部哨兵，用于递归链传递


class _FuncTracer:
    """
    单函数粒度的变量监控器
    只在「被装饰函数」的「line」事件触发检查，调用外部函数时自动暂停
    """

    __slots__ = ("cond", "varnames", "active", "owner_func_name", "retval")

    def __init__(self, cond: Callable, varnames: list[str], retval):
        self.cond = cond
        self.varnames = varnames
        self.active = False
        self.owner_func_name: Optional[str] = None
        self.retval = retval

    # ---------- 真正的检查 ----------
    def _check(self, frame: FrameType) -> bool:
        values = []
        for name in self.varnames:
            val = None
            try:
                # 1. 局部变量
                if name in frame.f_locals:
                    val = frame.f_locals[name]
                # 2. 全局变量
                elif name in frame.f_globals:
                    val = frame.f_globals[name]
                # 3. 类属性 / 私有属性  (含 name-mangling)
                elif "." in name:
                    part0, *parts = name.split(".")
                    obj = frame.f_locals[part0]
                    for attr in parts:
                        # 对双下划线属性做 mangle
                        if attr.startswith("__") and not attr.endswith("__"):
                            attr = f"_{obj.__class__.__name__}{attr}"
                        obj = getattr(obj, attr)
                    val = obj
                else:
                    raise NameError(name)
            except Exception:
                val = None
            values.append(val)

        # 条件函数内部再做一次容错，避免 None 参与比较
        try:
            return bool(self.cond(*values))
        except Exception:
            return False

    # ---------- trace 回调 ----------
    def _trace(self, frame: FrameType, event: str, arg: Any) -> Optional[Callable]:
        # 只在「所属函数」内工作
        if frame.f_code.co_name != self.owner_func_name:
            return None

        if event == "call":
            # 进入函数：激活检查
            self.active = True
            return self._trace

        if event == "return":
            # 离开函数：去激活
            self.active = False
            return self._trace

        if event == "line" and self.active:
            # 每条字节码之前检查
            if self._check(frame):
                # 满足条件：抛 StopIteration 给调用者
                raise StopIteration("Variable condition met")

        return self._trace

    # 根据 retval 类型计算真正要返回的值
    def _make_return(self, frame: FrameType):
        if self.retval is None:
            return None
        # 1. 直接字面量（int, list, dict, set, tuple...）
        if not isinstance(self.retval, str):
            return self.retval
        # 2. 字符串当成表达式，在 frame 上下文中求值
        try:
            # 构造局部命名空间：局部变量 + 全局变量
            namespace = frame.f_globals.copy()
            namespace.update(frame.f_locals)
            return eval(self.retval, namespace)
        except Exception:
            # 求值失败就返回 None
            return None


def monitor_variables(varnames: list[str], condition: Callable[[...], bool], retval = None):
    """
    装饰器：监控指定变量，条件为真时立即终止被装饰函数
    支持全局、局部、类属性、私有属性写法  ['x', 'self.__data', 'MyCls.counter']
    """

    def decorator(func: Callable) -> Callable:
        tracer = _FuncTracer(condition, varnames, retval)
        tracer.owner_func_name = func.__name__

        @functools.wraps(func)
        def wrapper(*args, **kw):
            # 保存旧 trace 函数
            old_trace = sys.gettrace()
            try:
                sys.settrace(tracer._trace)
                return func(*args, **kw)
            except StopIteration as e:
                if str(e) == "Variable condition met":
                    return tracer._make_return(sys._getframe(0).f_back)  # 拿到被终止函数帧
                raise
            finally:
                sys.settrace(old_trace)

        return wrapper

    return decorator


# -------------------------------------------------
# 使用示例（全局、类、局部、私有、递归、互调）
# -------------------------------------------------
if __name__ == "__main__":
    g = 100


    class Foo:
        cls_var = 0

        def __init__(self):
            self.__priv = 10

        # 监控类变量、私有属性、全局变量、局部变量
        @monitor_variables(
            ["g", "self.__priv", "Foo.cls_var", "tmp"],
            lambda g, priv, cls, tmp: g < 95 or priv <= 5 or cls >= 3 or tmp == 7
        )
        def work(self, x):
            global g
            print("---- enter work ----")
            for i in range(10):
                tmp = i + x  # 局部变量
                g -= 1
                self.__priv -= 1
                Foo.cls_var += 1
                print(f"i={i}  g={g}  __priv={self.__priv}  cls_var={Foo.cls_var}  tmp={tmp}")
                self.helper()  # 调用其他函数，内部不检查
            print("---- exit work ----")
            return "done"

        def helper(self):
            # 这里所有变量再怎么变化都不会触发检查
            Foo.cls_var += 100
            print("  (helper) cls_var += 100  ->", Foo.cls_var)
            Foo.cls_var -= 100


    # 递归场景
    @monitor_variables(["n"], lambda n: n == 9,retval = "n")
    def rec(n):
        print("rec", n)
        if n == 0:
            return 0
        return 1 + rec(n - 1)


    # 测试
    f = Foo()
    print("work return:", f.work(0))
    print()
    print("rec return:", rec(10))
