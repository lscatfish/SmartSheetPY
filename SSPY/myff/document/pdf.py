"""pdf解析"""
from SSPY.helperfunction import clean_space
from SSPY.myff.document.base import ParasSheets


class PdfParser:
    """解析Pdf的工具"""

    def __init__(self, path):
        self.__path = path

    @property
    def sheets(self):
        """表格"""
        import pdfplumber
        with pdfplumber.open(self.__path) as mypdf:
            if len(mypdf.pages) <= 0: return False
            tables = []
            for page in mypdf.pages:
                tables.extend(page.extract_tables())
            return tables

    @property
    def paragraphs(self):
        import fitz  # PyMuPDF
        try:
            pdf = fitz.open(self.__path)
            para: list[str] = []
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
                                p_text.append(clean_space(span["text"], ''))
                para.extend(p_text)
            return para
        except Exception as e:
            print(f'pdf文件"{self.__path}"解析失败：{e}，已跳过...')
            return []


class Pdf(ParasSheets):
    """解析Pdf"""

    def __init__(self, path):
        super().__init__(path)
        self.ftype = self.Type.pdf
        p = PdfParser(self._absolute_path)
        self.__parse_sheets(p)
        self.__parse_paragraphs(p)

    def __parse_sheets(self, p):
        self._sheets = p.sheets

    def __parse_paragraphs(self, p):
        self._paragraphs = p.paragraphs
