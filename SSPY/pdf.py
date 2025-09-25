import pdfplumber
import pypdfium2
from .helperfunction import *
from .mycell.rectcell import MyRectCell


class PdfLoad:
    """用于读取pdf文件"""

    def __init__(
        self,
        pdf_path: str = None,
        table_only: bool = True):
        self.__path = pdf_path
        self.__tableOnly = table_only
        self.__sheets = []
        self.__pageList = []
        if self.__tableOnly:
            self.__extract_tables()
        else:
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
            return self.__sheets
        else:
            return None

    @property
    def pages(self):
        return self.__pageList

    def get_pages(self, target_pagenum: list | int):
        if self.__tableOnly: return None
        if isinstance(target_pagenum, int):
            if len(self.__pageList) >= target_pagenum >= 1:
                return self.__pageList[target_pagenum - 1]
        if isinstance(target_pagenum, list):
            outp = []
            for i in target_pagenum:
                if isinstance(i, int):
                    if len(self.__pageList) >= i >= 1:
                        outp.append(self.__pageList[i - 1])
                else:
                    return None
            return outp
        return None

    def get_sheet(self, index = None):
        if not self.__tableOnly: return None
        if isinstance(index, int):
            if len(self.__sheets) > index:
                return self.__sheets[index]
        if isinstance(index, str):  # 按照关键值查找sheet
            for sheet in self.__sheets:
                if check_value(in_list = sheet, target_value = index, part = False): return sheet
        if isinstance(index, list):
            for sheet in self.__sheets:
                if check_value(in_list = sheet, target_value = index, part = True): return sheet
        return None

    def __extract_tables(self):
        with pdfplumber.open(self.__path) as mypdf:
            if len(mypdf.pages) <= 0: return False
            tables = []
            for page in mypdf.pages:
                tables.append(page.extract_tables())
            self.__sheets = clean_enter(tables)
        return True

    def __extract_text(self):
        pdf = pypdfium2.PdfDocument(self.__path)
        for page_num in range(len(pdf)):
            textpage = pdf[page_num].get_textpage()
            n_rects = textpage.count_rects()
            apage = []
            for i in range(n_rects):
                bbox = textpage.get_rect(i)
                text = textpage.get_text_bounded(*bbox)
                c = MyRectCell(text = text, left = bbox[0], bottom = bbox[1], right = bbox[2], top = bbox[3])
                apage.append(c)
            self.__pageList.append(apage)
        pdf.close()
