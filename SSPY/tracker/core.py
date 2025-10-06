import sys
from functools import wraps


class ExitWhenTriggered(Exception):
    """自定义异常：用于强制退出被监控函数"""
    pass


class VariableTracker:
    def __init__(self):
        self.enabled = False  # 追踪器总开关
        self.target_type = None  # 目标类型：local/self_attr/param
        self.target_key = None  # 目标标识（变量名/属性名/参数名）
        self.expected_value = None  # 预期值（支持固定值或条件函数）

    def set_local_variable(self, var_name, expected_value):
        """设置监控：函数局部变量（如 'count'）"""
        self.target_type = "local"
        self.target_key = var_name
        self.expected_value = expected_value
        self.enabled = True

    def set_self_attribute(self, attr_name, expected_value):
        """设置监控：类中self成员变量（如 'count'，对应 self.count）"""
        self.target_type = "self_attr"
        self.target_key = attr_name  # 仅传属性名，无需带'self.'
        self.expected_value = expected_value
        self.enabled = True

    def set_function_param(self, param_name, expected_value):
        """设置监控：函数输入参数（如 'user_id'）"""
        self.target_type = "param"
        self.target_key = param_name
        self.expected_value = expected_value
        self.enabled = True

    def disable(self):
        """关闭追踪器"""
        self.enabled = False

    def _get_current_value(self, frame):
        """根据目标类型，从当前执行帧中获取变量值"""
        if self.target_type == "local":
            # 局部变量：从函数局部变量表中读取
            return frame.f_locals.get(self.target_key, None)

        elif self.target_type == "self_attr":
            # self成员变量：先找self实例，再读属性
            self_instance = frame.f_locals.get("self", None)
            if self_instance is None:
                return None  # 非实例方法，无self

            attr_name = self.target_key
            # 处理私有变量（双下划线开头）：自动添加名称修饰
            if attr_name.startswith("__") and not attr_name.endswith("__"):
                # 获取当前类名（self实例所属的类）
                class_name = self_instance.__class__.__name__
                # 生成修饰后的名称：_类名__变量名
                mangled_attr = f"_{class_name}{attr_name}"
                attr_name = mangled_attr  # 替换为修饰后的名称

            # 支持多层属性（如 'foo.bar'）
            current = self_instance
            for attr in attr_name.split("."):
                current = getattr(current, attr, None)
                if current is None:
                    break
            return current

        elif self.target_type == "param":
            # 函数参数：参数本质是特殊的局部变量，直接从局部变量表读取
            return frame.f_locals.get(self.target_key, None)

        return None

    def _is_condition_met(self, current_value):
        """判断当前值是否满足预期条件"""
        if current_value is None:
            return False
        # 支持预期值为条件函数（如 lambda x: x > 5）
        if callable(self.expected_value):
            return self.expected_value(current_value)
        # 固定值匹配
        return current_value == self.expected_value

    def _trace_handler(self, frame, event, arg):
        """行级跟踪处理器：每执行一行代码时触发"""
        if not self.enabled or event != "line":
            return self._trace_handler  # 未启用或非行事件，直接返回

        # 获取当前变量值并检查条件
        current_value = self._get_current_value(frame)
        if self._is_condition_met(current_value):
            # 条件满足，抛出异常强制退出
            # print(f"\n[触发退出] {self.target_type} '{self.target_key}' = {current_value}")
            raise ExitWhenTriggered()

        return self._trace_handler

    def decorate(self, func):
        """装饰器：为目标函数添加监控逻辑"""

        @wraps(func)
        def wrapper(*args, **kwargs):
            # 保存原有跟踪器，注册当前处理器
            old_trace = sys.gettrace()
            sys.settrace(self._trace_handler)

            try:
                return func(*args, **kwargs)
            except ExitWhenTriggered:
                return  # 捕获退出异常，正常终止
            finally:
                # 恢复原有跟踪配置，避免影响其他代码
                sys.settrace(old_trace)

        return wrapper