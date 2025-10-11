"""
搜索类的基础工具
"""
import time

from SSPY.datastorage import *


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
        shared_int: str | None = self.connect_progress(self.__docx)
        if shared_int is None: return
        from SSPY.mydocx import DocxLoad

        length = len(self.__docx)
        for i in range(length):
            self.post_progress(i, length)
            file = DocxLoad(self.__docx[i], True, True, True)
            d = DOCXDataStorage(
                path = self.__docx[i],
                sheets = file.sheets,
                paragraphs = file.paragraphs)
            self.__datas.append(d)
        self.disconnect_progress()


    def preload_pdf(self):
        shared_int: str | None = self.connect_progress(self.__pdf)
        if shared_int is None: return
        from SSPY.mypdf import PdfLoad

        length = len(self.__pdf)
        for i in range(len(self.__pdf)):
            self.post_progress(i, length)
            file = PdfLoad(self.__pdf[i], table_only = False)
            d = PDFDataStorage(
                path = self.__pdf[i],
                paragraphs = file.pages,
                sheets = file.sheets)
            self.__datas.append(d)
        self.disconnect_progress()



    def preload_xlsx(self):
        shared_int: str | None = self.connect_progress(self.__xlsx)
        if shared_int is None: return
        from SSPY.myxlsx import XlsxLoad

        length = len(self.__xlsx)
        for i in range(len(self.__xlsx)):
            self.post_progress(i, length)
            file = XlsxLoad(
                self.__xlsx[i],
                const_classname = False)
            d = XLSXDataStorage(
                path = self.__xlsx[i],
                sheets = file.sheets)
            self.__datas.append(d)
        self.disconnect_progress()

    def connect_progress(self, in_list: list[str] | None):
        """链接到进度条"""
        if not (isinstance(in_list, list) and len(in_list) > 0): return None

        from SSPY.communitor.core import get_response
        while True:
            response, shared_int = get_response(('request_progress_gauge', len(in_list)))
            if response == 'wait':
                if isinstance(shared_int, int):
                    time.sleep(abs(shared_int))
            elif response == 'done':
                return 'done'
            else:
                raise ValueError(f'main thread response error : response = {response}')

    def disconnect_progress(self):
        """取消进度条的链接"""
        from SSPY.communitor.core import get_response
        get_response('close_progress_gauge')


    def post_progress(self, now_idx, max_idx):
        """发布进度信息"""
        from SSPY.communitor.core import get_response
        get_response(('progress_now', now_idx, max_idx))

    def clear(self):
        self.__root_dir = ''
        self.__folder = None
        self.__docx.clear()
        self.__pdf.clear()
        self.__xlsx.clear()
        self.__datas.clear()

    def find(self, target: str, rst: list):
        """
        搜索所有
        Args:
            target:搜索目标
            rst:搜索结果
        """
        # from SSPY.communitor.core import get_response
        if isinstance(target, str) and target == '':
            return
        for d in self.__datas:
            rst.extend(d.find_value(target))
