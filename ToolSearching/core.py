"""
搜索类的基础工具
"""
import anyio


class SearchingTool:
    """搜索工具"""

    def __init__(self, root_dir = './input/'):
        """我们还是选择预加载所有数据"""
        from .datastorage import DataStorager
        from SSPY.globalconstants import GlobalConstants as gc
        from SSPY.myfolder import DefFolder
        self.__folder = DefFolder(root_dir)
        self.__docx: list[str] = self.__folder.get_paths_by(gc.extensions_DOCX)
        self.__pdf: list[str] = self.__folder.get_paths_by(gc.extensions_PDF)
        self.__xlsx: list[str] = self.__folder.get_paths_by(gc.extensions_XLSX)
        self.__datas: list[DataStorager] = []

    def preload(self):
        """预加载所有数据，总控制函数"""
        pass

    def preload_docx(self):
        from SSPY.communitor.sharedvalue import SharedInt
        from SSPY.mydocx import DocxLoad

        shared_int: SharedInt | None = self.connect_progress(self.__docx)
        if shared_int is None: return

        for i in range(len(self.__docx)):
            shared_int.int1 = i
            dfile = DocxLoad(self.__docx[i], True, True, True)

        pass

    def preload_pdf(self):
        pass

    def preload_xlsx(self):
        pass

    def connect_progress(self, in_list: list[str] | None):
        """链接到进度条"""
        if not (isinstance(in_list, list) and len(in_list) > 0): return None

        from SSPY.communitor.core import get_response
        from SSPY.communitor.sharedvalue import SharedInt

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
