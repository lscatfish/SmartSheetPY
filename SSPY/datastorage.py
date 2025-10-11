"""数据储存类"""
from copy import deepcopy
from enum import Enum, unique


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


class XLSXDataStorage(BaseDataStorage):
    """xlsx中的解析方式"""

    def __init__(self, path: str, sheets: list[list[list[str]]]):
        super().__init__(path, DataType.pdf)
        self._sheets = sheets

    @property
    def sheets(self) -> list[list[list[str]]]:
        return deepcopy(self._sheets)


class DOCXDataStorage(BaseDataStorage):
    def __init__(self, path: str, sheets: list[list[list[str]]], paragraphs: list[str]):
        super().__init__(path, DataType.docx)
        self.__paragraphs = paragraphs
        self._sheets = sheets

    @property
    def paragraphs(self) -> list[str]:
        return deepcopy(self.__paragraphs)

    @property
    def sheets(self) -> list[list[list[str]]]:
        return deepcopy(self._sheets)
