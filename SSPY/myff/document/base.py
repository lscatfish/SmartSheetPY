"""基础方式"""
from copy import deepcopy

from SSPY.myff.base import BaseFile, calculate_str_hash
from SSPY.helperfunction import clean_enter, clean_space, all_str


class ParasSheets(BaseFile):
    """定义段落与表格"""

    def __init__(self, path: str):
        super().__init__(path)
        self._sheets: list[list[list[str]]] | None = None
        """表格"""
        self._paragraphs: list[list[str]] | list[str] | None = None
        """段落"""
        self.__hash = None
        """有效哈希值"""

    def chash(self) -> str:
        para = all_str(clean_enter(clean_space(self._paragraphs, ''), ''), '')

        if self.ftype == self.Type.docx:
            sh = all_str(clean_enter(clean_space(self._sheets, ''), ''), '')
            if len(para) == 0 and 0 == len(sh):
                return self.hash_all
            hash1 = calculate_str_hash(para)
            hash2 = calculate_str_hash(sh)
            return calculate_str_hash(hash1 + hash2)
        elif self.ftype == self.Type.pdf:
            if len(para) == 0:
                return self.hash_all
            hash1 = calculate_str_hash(para)
            return hash1
        else:
            return self.hash_all

    def is_same_content(self, other: 'ParasSheets') -> bool:
        return (self._absolute_path == other._absolute_path) or (self.hash == other.hash)

    @property
    def hash(self):
        if self.__hash is None:
            self.__hash = self.chash()
        return self.__hash

    @property
    def sheets(self) -> list[list[list[str]]] | None:
        """获取表格"""
        if len(self._sheets) == 0:
            return None
        return clean_enter(clean_space(self._sheets, ''), '')

    @property
    def paragraphs(self) -> list[list[list[str]]] | list[list[str]] | None:
        """段落"""
        if len(self._paragraphs) == 0:
            return None
        return clean_enter(clean_space(self._paragraphs, ''), '')

    def _auto_choose(self):
        """自动筛选出表格的类型"""
        from SSPY.fuzzy.search import searched_recursive
        from SSPY.globalconstants import GlobalConstants as gc
        for s in self.sheets:
            if searched_recursive(gc.chstrSignPosition, s, target_as_sub = True):
                """班委"""
                return s, 'cmtt'
            elif searched_recursive(gc.chstrPosition, s, target_as_sub = False):
                """学员"""
                return s, 'clmt'
        return None, None

    def _trans(self, key_sheet):
        """转化方法"""
        from SSPY.PersonneInformation import DefPerson
        per = DefPerson()
        for row in key_sheet:
            i = 0
            while i < len(row):
                stdkey = DefPerson.get_stdkey(row[i], inkey_as_sub = True)
                if stdkey is not None:
                    i += 1
                    while i < len(row):
                        if row[i] == 'None':
                            i += 1
                        else:
                            per.set_information(stdkey, row[i])
                            i += 1
                            break
                else:
                    i += 1

        per.filepath = {self.hash: self._absolute_path}

        if '推荐' in self._relative_path:
            per.set_information('报名方式', '组织推荐')
        elif '自' in self._relative_path:
            per.set_information('报名方式', '自主报名')
        elif '组织' in self._relative_path or '社团' in self._relative_path or '学院' in self._relative_path:
            per.set_information('报名方式', '组织推荐')
        elif '重庆大学团校' in self._relative_path or '团校报名' in self._relative_path or '团校学员报名' in self._relative_path:
            per.set_information('报名方式', '自主报名')
        else:
            # 不以最坏情况思考
            per.set_information('报名方式', '组织推荐')
        per.optimize()
        return per

    @property
    def person(self):
        """返回一个人员的信息"""
        key_sheet, key_way = self._auto_choose()
        if key_sheet is None:
            return None
        per = self._trans(key_sheet)
        if key_way == 'cmtt':
            per.ifsign = True
        return per
