"""
搜索类的基础工具
"""
from SSPY.datastorage import *
from SSPY.communitor.sharedvalue import SharedInt


class SearchingTool:
    """搜索工具"""

    def __init__(self):
        """我们还是选择预加载所有数据"""
        self.__root_dir = ''
        self.__folder = None
        self.__docx: list[str] = []
        self.__pdf: list[str] = []
        self.__xlsx: list[str] = []
        self.__datas: list[BaseDataStorage | DOCXDataStorage | PDFDataStorage | XLSXDataStorage] = []

    def start(self, root_dir = './input/'):
        from SSPY.globalconstants import GlobalConstants as gc
        from SSPY.myfolder import DefFolder
        self.__root_dir = root_dir
        self.__folder = DefFolder(root_dir)
        self.__docx: list[str] = self.__folder.get_paths_by(gc.extensions_DOCX)
        self.__pdf: list[str] = self.__folder.get_paths_by(gc.extensions_PDF)
        self.__xlsx: list[str] = self.__folder.get_paths_by(gc.extensions_XLSX)
        self.__datas: list[BaseDataStorage | DOCXDataStorage | PDFDataStorage | XLSXDataStorage] = []
        self.preload()

    def preload(self):
        """预加载所有数据，总控制函数"""
        self.preload_docx()
        self.preload_pdf()
        self.preload_xlsx()

    def preload_docx(self):
        shared_int: SharedInt | None = self.connect_progress(self.__docx)
        if shared_int is None: return
        from SSPY.mydocx import DocxLoad

        for i in range(len(self.__docx)):
            shared_int.int1 = i
            file = DocxLoad(self.__docx[i], True, True, True)
            d = DOCXDataStorage(
                path = self.__docx[i],
                sheets = file.sheets,
                paragraphs = file.paragraphs)
            self.__datas.append(d)
        shared_int.int2 = 0  # 让progress能够正常退出


    def preload_pdf(self):
        shared_int: SharedInt | None = self.connect_progress(self.__pdf)
        if shared_int is None: return
        from SSPY.mypdf import PdfLoad

        for i in range(len(self.__pdf)):
            shared_int.int1 = i
            file = PdfLoad(self.__pdf[i], table_only = False)
            d = PDFDataStorage(
                path = self.__pdf[i],
                paragraphs = file.pages,
                sheets = file.sheets)
            self.__datas.append(d)
        shared_int.int2 = 0


    def preload_xlsx(self):
        shared_int: SharedInt | None = self.connect_progress(self.__xlsx)
        if shared_int is None: return
        from SSPY.myxlsx import XlsxLoad

        for i in range(len(self.__xlsx)):
            shared_int.int1 = i
            file = XlsxLoad(
                self.__xlsx[i],
                const_classname = False)
            d = XLSXDataStorage(
                path = self.__xlsx[i],
                sheets = file.sheets)
            self.__datas.append(d)
        shared_int.int2 = 0

    def connect_progress(self, in_list: list[str] | None):
        """链接到进度条"""
        if not (isinstance(in_list, list) and len(in_list) > 0): return None

        from SSPY.communitor.core import get_response
        import asyncio
        while True:
            response, shared_int = get_response(('request_progress_gauge', len(in_list)))
            if response == 'wait':
                if isinstance(shared_int, int):
                    asyncio.sleep(abs(shared_int))
            elif response == 'done' and isinstance(shared_int, SharedInt):
                break
            else:
                raise ValueError(f'main thread response error : response = {response}')
        return shared_int

    def clear(self):
        self.__root_dir = ''
        self.__folder = None
        self.__docx.clear()
        self.__pdf.clear()
        self.__xlsx.clear()
        self.__datas.clear()

    def find(self, target: str):
        """搜索所有"""
        rst = []
        if isinstance(target, str) and target == '':
            return rst
        for d in self.__datas:
            rst.extend(d.find_value(target))
        return rst
