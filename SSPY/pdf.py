import pdfplumber
from helperfunction import *


class PdfLoad:
    """用于读取pdf文件"""

    def __init__(
        self,
        pdf_path: str = None,
        table_only: bool = True):
        self.__path = pdf_path
        self.__tableOnly = table_only
        self.__sheets = []
        if self.__tableOnly:
            self.__extract_tables()

    @property
    def path(self):
        return self.__path

    @path.setter
    def path(self, path: str):
        self.__path = path

    @property
    def sheets(self):
        return self.__sheets

    def get_sheet(self, index = None):
        if isinstance(index, int):
            if len(self.__sheets) > index:
                return self.__sheets[index]
        if isinstance(index, str):  # 按照关键值查找sheet
            for sheet in self.__sheets:
                if check_value(in_list = sheet, target_value = index, part = False): return sheet
        return None

    def __extract_tables(self):
        with pdfplumber.open(self.__path) as mypdf:
            if len(mypdf.pages) <= 0: return False
            tables = []
            for page in mypdf.pages:
                tables.append(page.extract_tables())
            self.__sheets = clean_enter(tables)
        return True


a = PdfLoad('./组织推荐班委-李炘宇.pdf')
print(a.get_sheet('姓'))
