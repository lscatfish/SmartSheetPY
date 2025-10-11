"""
搜索类的基础工具
"""
import anyio
from SSPY.datastorage import *
from SSPY.communitor.sharedvalue import SharedInt


class SearchingTool:
    """搜索工具"""

    def __init__(self, root_dir = './input/'):
        """我们还是选择预加载所有数据"""
        from SSPY.globalconstants import GlobalConstants as gc
        from SSPY.myfolder import DefFolder
        self.__folder = DefFolder(root_dir)
        self.__docx: list[str] = self.__folder.get_paths_by(gc.extensions_DOCX)
        self.__pdf: list[str] = self.__folder.get_paths_by(gc.extensions_PDF)
        self.__xlsx: list[str] = self.__folder.get_paths_by(gc.extensions_XLSX)
        self.__datas: list[BaseDataStorage | DOCXDataStorage | PDFDataStorage | XLSXDataStorage] = []

    def preload(self):
        """预加载所有数据，总控制函数"""
        pass

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

        while True:
            response, shared_int = get_response(('request_progress_gauge', len(in_list)))
            if response == 'wait':
                if isinstance(shared_int, int):
                    anyio.sleep(abs(shared_int))
            elif response == 'done' and isinstance(shared_int, SharedInt):
                break
            else:
                raise ValueError(f'main thread response error : response = {response}')
        return shared_int
