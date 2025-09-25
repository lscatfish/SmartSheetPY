import pdfplumber
import pypdfium2
from helperfunction import *
from basic import Point


class MyCell:
    """定义一个单元格地址和内容"""

    def __init__(
        self,
        text: str = None,
        left: float = None,
        top: float = None,
        right: float = None,
        bottom: float = None, ):
        self.__text = text
        self.__left = left
        self.__top = top
        self.__right = right
        self.__bottom = bottom

    @property
    def text(self):
        return self.__text

    @text.setter
    def text(self, value: str):
        self.__text = value

    @property
    def left(self):
        return self.__left

    @left.setter
    def left(self, value: float):
        self.__left = value

    @property
    def top(self):
        return self.__top

    @top.setter
    def top(self, value: float):
        self.__top = value

    @property
    def right(self):
        return self.__right

    @right.setter
    def right(self, value: float):
        self.__right = value

    @property
    def bottom(self):
        return self.__bottom

    @bottom.setter
    def bottom(self, value: float):
        self.__bottom = value

    @property
    def top_left(self):
        return Point(self.__left, self.__top)

    @top_left.setter
    def top_left(self, value: Point):
        self.__left = value.x
        self.__top = value.y

    @property
    def top_right(self):
        return Point(self.__right, self.__bottom)

    @top_right.setter
    def top_right(self, value: Point):
        self.__right = value.x
        self.__bottom = value.y

    @property
    def bottom_left(self):
        return Point(self.__left, self.__top)

    @bottom_left.setter
    def bottom_left(self, value: Point):
        self.__left = value.x
        self.__top = value.y

    @property
    def bottom_right(self):
        return Point(self.__right, self.__bottom)

    @bottom_right.setter
    def bottom_right(self, value: Point):
        self.__right = value.x
        self.__bottom = value.y


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

            for i in range(n_rects):
                bbox = textpage.get_rect(i)

            text_all = textpage.get_text_bounded()
            self.__pageList.append(text_all)
        pdf.close()

        # with pdfium.PdfDocument(self.__path) as doc:
        #     for page in doc.pages:
        #         page_text = page.get_text()
        #         self.__pageList.append(page_text)


a = PdfLoad('./组织推荐班委-李炘宇.pdf', table_only = False)
print(a.pages)
