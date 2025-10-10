"""
搜索类的基础工具
"""


class SearchingTool:
    """搜索工具"""

    def __init__(self, root_dir = './input/'):
        """我们还是选择预加载所有数据"""
        from SSPY.globalconstants import GlobalConstants as gc
        from SSPY.myfolder import DefFolder
        self.__folder = DefFolder(root_dir)
        self.__docx: list[str] = self.__folder.get_paths_by(gc.extensions_DOCX)
        self.__pdf: list[str] = self.__folder.get_paths_by(gc.extensions_PDF)
        self.__xlsx = self.__folder.get_paths_by(gc.extensions_XLSX)
    def preload(self):
        """预加载所有数据，总控制函数"""
        pass
    def preload_docx(self):
        pass
    def preload_pdf(self):
        pass
    def preload_xlsx(self):
        pass
