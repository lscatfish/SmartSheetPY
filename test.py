import sys
import inspect
from enum import Enum
from types import FunctionType
import threading

# 线程局部存储用于保存当前监控器
_thread_local = threading.local()


def get_current_monitor():
    """获取当前线程的监控器实例"""
    return getattr(_thread_local, 'current_monitor', None)


class VariableType(Enum):
    LOCAL = 1
    GLOBAL = 2
    INSTANCE_PUBLIC = 3
    INSTANCE_PRIVATE = 4
    CLASS_PUBLIC = 5
    CLASS_PRIVATE = 6
    ARGUMENT = 7


class MonitorExit(Exception):
    """自定义异常用于终止被监控函数，携带特定返回值"""

    def __init__(self, return_value):
        self.return_value = return_value
        super().__init__("Condition met")


class VariableMonitor:
    def __init__(self, target_var, var_type, condition, return_value):
        """
        :param target_var: 要监控的变量名
        :param var_type: 变量类型 (VariableType)
        :param condition: 条件检测函数，接受变量值，返回bool
        :param return_value: 条件满足时返回的值
        """
        self.target_var = target_var
        self.var_type = var_type
        self.condition = condition
        self.return_value = return_value
        self.original_trace = None
        self.target_frames = set()
        self.nested_functions = {}  # 存储嵌套函数的代码对象和返回值映射

    def __enter__(self):
        """启用监控"""
        self.original_trace = sys.gettrace()
        sys.settrace(self.global_trace)
        # 设置当前线程的监控器
        _thread_local.current_monitor = self
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """禁用监控并处理异常"""
        sys.settrace(self.original_trace)
        # 清除当前线程的监控器
        if hasattr(_thread_local, 'current_monitor'):
            del _thread_local.current_monitor
        if exc_type is MonitorExit:
            return True  # 抑制MonitorExit异常

    def global_trace(self, frame, event, arg):
        """全局跟踪函数"""
        if event != 'call':
            return None

        # 检查是否进入目标函数或嵌套函数
        if frame.f_code in self.target_frames or frame.f_code in self.nested_functions:
            return self.local_trace
        return None

    def local_trace(self, frame, event, arg):
        """局部跟踪函数"""
        if event == 'line':
            # 在每行代码执行前检查条件
            if self.check_condition(frame):
                # 获取当前函数的返回值
                return_value = self.nested_functions.get(frame.f_code, self.return_value)
                raise MonitorExit(return_value)
        elif event == 'return':
            # 函数结束时移除栈帧
            self.target_frames.discard(frame.f_code)
            if frame.f_code in self.nested_functions:
                del self.nested_functions[frame.f_code]

        return self.local_trace

    def get_variable_value(self, frame):
        """根据变量类型获取变量值"""
        try:
            if self.var_type == VariableType.LOCAL:
                return frame.f_locals.get(self.target_var)

            elif self.var_type == VariableType.GLOBAL:
                return frame.f_globals.get(self.target_var)

            elif self.var_type == VariableType.ARGUMENT:
                # 检查参数变量
                code = frame.f_code
                arg_names = code.co_varnames[:code.co_argcount]
                if self.target_var in arg_names:
                    return frame.f_locals.get(self.target_var)
                return None

            elif self.var_type in (VariableType.INSTANCE_PUBLIC, VariableType.INSTANCE_PRIVATE):
                # 获取实例变量
                if 'self' in frame.f_locals:
                    instance = frame.f_locals['self']
                    if self.var_type == VariableType.INSTANCE_PUBLIC:
                        return getattr(instance, self.target_var, None)
                    else:  # 私有变量
                        # 尝试访问私有变量（名称修饰）
                        private_name = f"_{instance.__class__.__name__}{self.target_var}"
                        return getattr(instance, private_name, None)
                return None

            elif self.var_type in (VariableType.CLASS_PUBLIC, VariableType.CLASS_PRIVATE):
                # 获取类变量
                if 'self' in frame.f_locals:
                    cls = frame.f_locals['self'].__class__
                elif 'cls' in frame.f_locals:
                    cls = frame.f_locals['cls']
                else:
                    return None

                if self.var_type == VariableType.CLASS_PUBLIC:
                    return getattr(cls, self.target_var, None)
                else:  # 私有类变量
                    private_name = f"_{cls.__name__}{self.target_var}"
                    return getattr(cls, private_name, None)

            return None
        except Exception:
            return None

    def check_condition(self, frame):
        """执行条件检测"""
        try:
            value = self.get_variable_value(frame)
            return value is not None and self.condition(value)
        except Exception:
            return False

    def add_nested_function(self, return_value = None):
        """添加嵌套函数到监控列表，并指定返回值"""

        def decorator(func):
            if isinstance(func, FunctionType):
                self.nested_functions[func.__code__] = return_value
            return func

        return decorator


def monitor_variables(target_var, var_type, condition, return_value = None):
    """
    装饰器：监控函数中的变量条件

    :param target_var: 要监控的变量名
    :param var_type: 变量类型 (VariableType)
    :param condition: 条件检测函数，接受变量值，返回bool
    :param return_value: 条件满足时返回的值
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            # 获取函数的代码对象用于标识
            code_obj = func.__code__

            with VariableMonitor(target_var, var_type, condition, return_value) as vm:
                # 添加目标函数的标识
                vm.target_frames.add(code_obj)
                try:
                    return func(*args, **kwargs)
                except MonitorExit as e:
                    return e.return_value

        return wrapper

    return decorator


# 使用示例：在嵌套函数中监控同一个实例变量，但使用不同的返回值
class NestedTest:
    def __init__(self):
        self.__t = 0  # 私有实例变量
        self.__stopFlag = False

    @monitor_variables(
        target_var = '__stopFlag',
        var_type = VariableType.INSTANCE_PRIVATE,
        condition = lambda x: x is True,
        return_value = "Main function stopped"
    )
    def main_method(self):
        print("Main method started")
        self.__t = 1

        # 获取当前监控器
        current_monitor = get_current_monitor()
        if current_monitor:
            # 定义嵌套函数并注册到监控器，指定不同的返回值
            @current_monitor.add_nested_function(return_value = "Nested function stopped")
            def ainq():
                print("Nested function started")
                # 在嵌套函数中访问私有变量
                print(f"Current __stopFlag: {self.__stopFlag}")
                # 修改私有变量
                self.__t = 10
                print("Nested function completed")

        print(f"Before calling ainq: __t = {self.__t}")
        ainq()
        print(f"After calling ainq: __t = {self.__t}")

        return "Main method completed"


# 测试
if __name__ == "__main__":
    print("Testing nested function monitoring with custom return values:")
    obj = NestedTest()

    # 测试在嵌套函数中触发停止条件
    print("\nTest 1: Trigger stop in nested function")


    # 在嵌套函数中设置停止标志
    def set_stop_in_nested():
        obj.__stopFlag = True


    # 替换嵌套函数以设置停止标志
    original_main = obj.main_method


    def modified_main():
        current_monitor = get_current_monitor()
        if current_monitor:
            @current_monitor.add_nested_function(return_value = "Nested function stopped")
            def ainq():
                print("Nested function started")
                set_stop_in_nested()  # 在嵌套函数中设置停止标志
                print("Nested function completed")
        return original_main()


    obj.main_method = modified_main
    result = obj.main_method()
    print(f"Result: {result}")  # 应该输出 "Nested function stopped"

    # 测试在主函数中触发停止条件
    print("\nTest 2: Trigger stop in main function")
    obj.main_method = original_main  # 恢复原始方法
    obj.__stopFlag = True  # 在主函数执行前设置停止标志
    result = obj.main_method()
    print(f"Result: {result}")  # 应该输出 "Main function stopped"