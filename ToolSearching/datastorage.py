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


class DataStorager:
    """数据储存类"""

    def __init__(
        self,
        path: str,
        datatype: DataType,
        sheets: list[list[list[str]]] | None = None,
        paragraphs: list[str] | None = None):
        """
        Args:
            path:路径
            datatype:数据类型
            sheets:表格
            paragraphs:文段
        """
        self.__path = path
        self.__datatype = datatype
        self.__sheets = sheets
        self.__paragraphs = paragraphs

    @property
    def path(self) -> str:
        """文件路径"""
        return self.__path

    @property
    def datatype(self) -> DataType:
        """文件类型"""
        return self.__datatype

    @property
    def sheets(self) -> list[list[list[str]]] | None:
        """文件的sheets"""
        return deepcopy(self.__sheets)

    @property
    def paragraphs(self) -> list[str] | None:
        """文段"""
        return deepcopy(self.__paragraphs)
