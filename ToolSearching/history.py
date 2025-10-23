"""历史搜索记录"""
import copy
from copy import deepcopy


class ASearch:
    """一次搜索的结果"""

    def __init__(self, target: str, root: str, rst: list[tuple]):
        """
        Args:
            target:搜索目标
            root:搜索子路径
            rst:搜索结果(二元)
        """
        self.__target = target
        self.__root = root
        self.__rst = copy.deepcopy(rst)

    @property
    def target(self):
        """搜索值"""
        return self.__target

    @property
    def root(self):
        """搜索的根路径"""
        return self.__root

    @property
    def rst(self):
        """搜索的结果"""
        return deepcopy(self.__rst)

    def is_same(self, target: str, root: str):
        """判断是否为同一次搜索"""
        return target == self.__target and root == self.__root

    def get_rst_by(self, target: str, root: str, return_val = None):
        """按照同直接拉取结果"""
        if self.is_same(target, root): return self.rst
        return return_val


class HistorySearch:
    """历史搜索记录"""

    def __init__(self):
        """最多保存100条"""
        self.__history: list[ASearch] = []

    def push_back(self, _in: ASearch):
        if self.has_history(_in.target, _in.root): return
        if len(self.__history) == 100:
            self.__history.pop(0)
        self.__history.append(_in)

    def has_history(self, target: str, root: str):
        for i in self.__history:
            if i.is_same(target, root): return True
        return False

    def get_history(self, target: str, root: str, return_val = None):
        """拉取一个值"""
        for i in self.__history:
            s = i.get_rst_by(target, root)
            if s: return s
        return return_val

    def save_all(self):
        """保存所有的搜索历史"""

        def _table():
            """转换为表格形式"""
            sh: list[list[str]] = [['搜索目标', '原文', '文件位置']]
            for asr in self.__history:
                for t in asr.rst:
                    if len(t) > 0:
                        line = [asr.target, t[0], t[1]]
                    else:
                        line = [asr.target, '', '']
                    sh.append(line)
            return sh

        def _save(sh):
            from SSPY.globalconstants import GlobalConstants as gc
            from SSPY.myxlsx import XlsxWrite
            from SSPY.myfolder import create_nested_folders
            create_nested_folders('./output/', if_print = False)  # 确保文件夹存在

            from datetime import datetime
            current_time = datetime.now()
            # 格式化示例（常用格式符：%Y-年，%m-月，%d-日，%H-时(24h)，%M-分，%S-秒）
            formatted_time = current_time.strftime("%m%d%H%M%S")
            XlsxWrite(
                path = f'./output/search_log{formatted_time}.xlsx',
                sheet = sh,
                widths = [30, 80],
                alignment = gc.alignmentLeft
            ).write()

        _save(_table())
        self.__history.clear()
