"""数据储存类"""
from copy import deepcopy
from enum import Enum, unique
from SSPY.fuzzy.search import search_recursive


@unique
class DataType(Enum):
    """数据类型"""
    docx = 1
    """docx文件"""
    pdf = 2
    """pdf文件类型"""
    xlsx = 3
    """xlsx文件类型"""


class BaseDataStorage:
    """数据储存基础类"""

    def __init__(
        self,
        path: str,
        datatype: DataType):
        """
        Args:
            path:路径
            datatype:数据类型
        """
        self.__path = path
        self.__datatype = datatype

    @property
    def path(self) -> str:
        """文件路径"""
        return self.__path

    @property
    def datatype(self) -> DataType:
        """文件类型"""
        return self.__datatype

    def find_value(self, target: str):
        """寻找目标量，按照(原文，路径)构建"""
        # 构建回复量
        f = []
        if target in self.__path:
            f = [(self.__path, self.__path)]
        return f

    def _deduplication(self, in_list: list[tuple]):
        """对一个list去重"""
        self
        if len(in_list) <= 1: return in_list
        dedup: list[tuple] = []
        exclude_index = []
        for i in range(len(in_list)):
            if i in exclude_index: continue
            dedup.append(in_list[i])
            for j in range(i + 1, len(in_list)):
                if in_list[i][0] == in_list[j][0] and in_list[i][1] == in_list[j][1]:
                    exclude_index.append(j)
        return dedup


class PDFDataStorage(BaseDataStorage):
    """PDF中文本的解析类型"""

    def __init__(self, path: str, sheets: list[list[list[str]]], paragraphs: list[list[str]]):
        super().__init__(path, datatype = DataType.pdf)
        self.__paragraphs = paragraphs
        self.__sheets = sheets

    @property
    def paragraphs(self) -> list[list[str]]:
        return deepcopy(self.__paragraphs)

    @property
    def sheets(self) -> list[list[list[str]]]:
        return deepcopy(self.__sheets)

    def find_value(self, target: str):
        likely: list[tuple] = []
        sp = super().find_value(target)
        if sp is not None: likely.extend(sp)
        for ans in search_recursive(target, self.__sheets, target_as_sub = True):
            st = (ans, self.path)
            likely.append(st)
        for ans in search_recursive(target, self.__paragraphs, target_as_sub = True):
            st = (ans, self.path)
            likely.append(st)
        likely = super()._deduplication(likely)
        return likely


class XLSXDataStorage(BaseDataStorage):
    """xlsx中的解析方式"""

    def __init__(self, path: str, sheets: list[list[list[str]]]):
        super().__init__(path, DataType.pdf)
        self.__sheets = sheets

    @property
    def sheets(self) -> list[list[list[str]]]:
        return deepcopy(self.__sheets)

    def find_value(self, target: str):
        likely: list[tuple] = []
        sp = super().find_value(target)
        if sp is not None: likely.extend(sp)
        for ans in search_recursive(target, self.__sheets, target_as_sub = True):
            st = (ans, self.path)
            likely.append(st)
        likely = super()._deduplication(likely)
        return likely


class DOCXDataStorage(BaseDataStorage):
    def __init__(self, path: str, sheets: list[list[list[str]]], paragraphs: list[str]):
        super().__init__(path, DataType.docx)
        self.__paragraphs = paragraphs
        self.__sheets = sheets

    @property
    def paragraphs(self) -> list[str]:
        return deepcopy(self.__paragraphs)

    @property
    def sheets(self) -> list[list[list[str]]]:
        return deepcopy(self.__sheets)

    def find_value(self, target: str):
        likely: list[tuple] = []
        sp = super().find_value(target)
        if sp is not None: likely.extend(sp)
        for ans in search_recursive(target, self.__sheets, target_as_sub = True):
            st = (ans, self.path)
            likely.append(st)
        for ans in search_recursive(target, self.__paragraphs, target_as_sub = True):
            st = (ans, self.path)
            likely.append(st)
        likely = super()._deduplication(likely)
        return likely
