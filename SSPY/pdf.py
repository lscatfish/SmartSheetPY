import pdfplumber
from helperfunction import *

with pdfplumber.open('./组织推荐班委-李炘宇.pdf') as pdf:
    page = pdf.pages[0]
    tables = page.extract_tables()
    for table in tables:
        af_table = clean_enter(table)
        for row in af_table:
            print(row)


class PdfLoad:
    """用于读取pdf文件"""

    def __init__(
        self,
        pdf_path: str = None,
        table_only: bool = True):
        self.__path = pdf_path
        self.__tableOnly = table_only
