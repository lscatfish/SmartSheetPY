# -*- coding: utf-8 -*-
"""共享变量访问器"""
import inspect
import threading
from copy import deepcopy


class BaseSharedValue:
    """共享变量访问器"""

    def __init__(self):
        self.rlock = threading.RLock()
        self.__default_value: dict[str, ...] = {}  # 使用

    @property
    def default_value(self):
        with self.rlock:
            return deepcopy(self.__default_value)

    # 这是不允许的行为
    # @default_value.setter
    # def default_value(self, value: list):
    #     with self.rlock:
    #         if isinstance(value, list):
    #             self.__default_value = deepcopy(value)

    def get_value(self, value_name: str):
        """变量名称必须是str"""
        with self.rlock:
            if isinstance(value_name, str):
                return self.__default_value.get(value_name, None)
            else:
                raise TypeError('BaseSharedValue: value_name must be str')

    def set_value(self, value_name: str, value, _ = None):
        """变量名称必须是str"""
        with self.rlock:
            if isinstance(value_name, str):
                self.__default_value[value_name] = value
            else:
                raise TypeError('BaseSharedValue: value_name must be str')

    def del_value(self, value_name: str):
        """删除一个变量"""
        with self.rlock:
            if isinstance(value_name, str):
                if value_name in self.__default_value:
                    self.__default_value.pop(value_name, None)
            else:
                raise TypeError('BaseSharedValue: value_name must be str')

    def get_defined_value_names(self):
        with self.rlock:
            return [k for k in self.__default_value.keys()]


class SharedInt(BaseSharedValue):
    """共享的int变量，提供了int1-int5的三个快速操做变量"""

    def __init__(self):
        super().__init__()
        self.__int1 = 0
        self.__int2 = 0
        self.__int3 = 0
        self.__int4 = 0
        self.__int5 = 0

    def get_value(self, value_name: str):
        with self.rlock:
            return super().get_value(value_name)

    def set_value(self, value_name: str, value: int, type_ = int):
        with self.rlock:
            if not isinstance(value, int):
                raise TypeError('SharedInt: value must be int')
            if not isinstance(value_name, str):
                raise TypeError('SharedInt: value_name must be str')
            match value_name:
                case 'int1':
                    self.__int1 = value
                case 'int2':
                    self.__int2 = value
                case 'int3':
                    self.__int3 = value
                case 'int4':
                    self.__int4 = value
                case 'int5':
                    self.__int5 = value
                case _:
                    super().set_value(value_name, value)

    def del_value(self, value_name: str):
        with self.rlock:
            super().del_value(value_name)


    @property
    def int1(self):
        with self.rlock:
            return self.__int1

    @property
    def int2(self):
        with self.rlock:
            return self.__int2

    @property
    def int3(self):
        with self.rlock:
            return self.__int3

    @property
    def int4(self):
        with self.rlock:
            return self.__int4

    @property
    def int5(self):
        with self.rlock:
            return self.__int5

    @int1.setter
    def int1(self, value):
        with self.rlock:
            if isinstance(value, int):
                self.__int1 = value
            else:
                raise TypeError('SharedInt: value must be int')

    @int2.setter
    def int2(self, value):
        with self.rlock:
            if isinstance(value, int):
                self.__int2 = value
            else:
                raise TypeError('SharedInt: value must be int')

    @int3.setter
    def int3(self, value):
        with self.rlock:
            if isinstance(value, int):
                self.__int3 = value
            else:
                raise TypeError('SharedInt: value must be int')

    @int4.setter
    def int4(self, value):
        with self.rlock:
            if isinstance(value, int):
                self.__int4 = value
            else:
                raise TypeError('SharedInt: value must be int')

    @int5.setter
    def int5(self, value):
        with self.rlock:
            if isinstance(value, int):
                self.__int5 = value
            else:
                raise TypeError('SharedInt: value must be int')

# class SharedBool(BaseSharedValue):
#     """共享变量"""
#     def __init__(self):
#         super().__init__()
#         self.__bool1 = False
#         self.__bool2 = False
#         self.__bool3 = False
#         self.__bool4 = False
#         self.__bool5 = False
#     def get_value(self, value_name: str):
#         with self.rlock:
#             if isinstance(value_name, str):
#                 pass


class SharedFloat(BaseSharedValue):
    def __init__(self):
        super().__init__()
        self.__float1 = 0.0
        self.__float2 = 0.0
        self.__float3 = 0.0
        self.__float4 = 0.0
        self.__float5 = 0.0

    def get_value(self, value_name: str):
        with self.rlock:
            return super().get_value(value_name)

    def set_value(self, value_name: str, value: float, type_ = float):
        with self.rlock:
            if not isinstance(value, float):
                raise TypeError('SharedFloat: value must be float')
            if not isinstance(value_name, str):
                raise TypeError('SharedFloat: value_name must be str')
            match value_name:
                case 'float1':
                    self.__float1 = value
                case 'float2':
                    self.__float2 = value
                case 'float3':
                    self.__float3 = value
                case 'float4':
                    self.__float4 = value
                case 'float5':
                    self.__float5 = value
                case _:
                    super().set_value(value_name, value)

    def del_value(self, value_name: str):
        with self.rlock:
            super().del_value(value_name)

    @property
    def float1(self):
        with self.rlock:
            return self.__float1

    @property
    def float2(self):
        with self.rlock:
            return self.__float2

    @property
    def float3(self):
        with self.rlock:
            return self.__float3

    @property
    def float4(self):
        with self.rlock:
            return self.__float4

    @property
    def float5(self):
        with self.rlock:
            return self.__float5

    @float1.setter
    def float1(self, value):
        with self.rlock:
            if isinstance(value, float):
                self.__float1 = value
            else:
                raise TypeError('SharedFloat: value must be float')

    @float2.setter
    def float2(self, value):
        with self.rlock:
            if isinstance(value, float):
                self.__float2 = value
            else:
                raise TypeError('SharedFloat: value must be float')

    @float3.setter
    def float3(self, value):
        with self.rlock:
            if isinstance(value, float):
                self.__float3 = value
            else:
                raise TypeError('SharedFloat: value must be float')

    @float4.setter
    def float4(self, value):
        with self.rlock:
            if isinstance(value, float):
                self.__float4 = value
            else:
                raise TypeError('SharedFloat: value must be float')

    @float5.setter
    def float5(self, value):
        with self.rlock:
            if isinstance(value, float):
                self.__float5 = value
            else:
                raise TypeError('SharedFloat: value must be float')


class SharedAnyTypes(BaseSharedValue):
    """任意类型的共享变量"""

    def __init__(self):
        super().__init__()
        self.__value_type: dict[str, type] = {}  # 变量名+type

    def get_value(self, value_name: str):
        with self.rlock:
            return super().get_value(value_name)

    def set_value(self, value_name: str, value, type_ = None):
        with self.rlock:
            if not isinstance(value_name, str):
                raise TypeError('SharedAnyTypes: value_name must be str')
            if type_ is None and value_name in self.__value_type:
                if not isinstance(value, self.__value_type[value_name]):
                    raise TypeError(f'SharedAnyTypes: value must be {self.__value_type[value_name]}')
                super().set_value(value_name, value)
                return

            if not isinstance(value, type_):
                raise TypeError(f'SharedAnyTypes: value must be {type_}')
            if not inspect.isclass(type_):
                raise TypeError('SharedAnyTypes: type_ must be type')
            self.__value_type[value_name] = type_
            super().set_value(value_name, value)


    def del_value(self, value_name: str):
        with self.rlock:
            if not isinstance(value_name, str):
                raise TypeError('SharedAnyTypes: value_name must be str')
            if value_name in self.__value_type:
                del self.__value_type[value_name]
                super().del_value(value_name)

    def get_type(self, value_name: str):
        with self.rlock:
            if not isinstance(value_name, str):
                raise TypeError('SharedAnyTypes: value_name must be str')
            return self.__value_type.get(value_name, None)
