import copy

import pdfplumber
from .helperfunction import clean_enter, clean_space


class PdfLoad:
    """用于读取pdf文件"""

    def __init__(
        self,
        pdf_path: str = None,
        table_only: bool = True,
        if_print: bool = False):
        self.__if_print = if_print
        if if_print:
            print(pdf_path)
        self.__path = pdf_path
        self.__tableOnly = table_only
        self.__sheets = []
        self.__pageList = []
        if self.__tableOnly:
            self.__extract_tables()
        else:
            self.__extract_tables()
            self.__extract_text()

    @property
    def path(self):
        return self.__path

    @path.setter
    def path(self, path: str):
        self.__path = path

    @property
    def sheets(self):
        if self.__tableOnly:
            return copy.deepcopy(self.__sheets)
        else:
            return None

    @property
    def pages(self):
        return copy.deepcopy(self.__pageList)

    def get_pages(self, target_pagenum: list | int):
        if self.__tableOnly: return None
        if isinstance(target_pagenum, int):
            if len(self.__pageList) >= target_pagenum >= 1:
                return copy.deepcopy(self.__pageList[target_pagenum - 1])
        if isinstance(target_pagenum, list):
            outp = []
            for i in target_pagenum:
                if isinstance(i, int):
                    if len(self.__pageList) >= i >= 1:
                        outp.append(self.__pageList[i - 1])
                else:
                    return None
            return copy.deepcopy(outp)
        return None

    def get_sheet(self, index: int | str = None, part = False) -> list[list[str]] | None:
        """
        Args:
            index:按照关键词获取
            part:是否启用部分匹配
        Returns:
            具有特征值的一个表
        """
        from .fuzzy.search import searched_recursive as if_in
        if not self.__tableOnly: return None
        if isinstance(index, int):
            if len(self.__sheets) > index:
                return copy.deepcopy(self.__sheets[index])
        if isinstance(index, str):  # 按照关键值查找sheet
            for sheet in self.__sheets:
                if if_in(index, sheet, target_as_sub = part, lib_as_sub = part):
                    return copy.deepcopy(sheet)
        return None

    def __extract_tables(self):
        with pdfplumber.open(self.__path) as mypdf:
            if len(mypdf.pages) <= 0: return False
            tables = []
            for page in mypdf.pages:
                tables.extend(page.extract_tables())
            self.__sheets = clean_enter(tables)
        return True

    def __extract_text(self):
        import fitz  # PyMuPDF
        pdf = fitz.open(self.__path)
        for page_num in range(len(pdf)):
            p_text: list[str] = []
            page = pdf.load_page(page_num)
            # 关键步骤：以字典形式获取页面中的所有块信息
            blocks_dict = page.get_text("dict")
            for block in blocks_dict["blocks"]:
                if block["type"] == 0:
                    # 遍历块中的每一行和每一个span
                    for line in block["lines"]:
                        for span in line["spans"]:
                            p_text.append(clean_space(span["text"]))
            self.__pageList.append(p_text)
