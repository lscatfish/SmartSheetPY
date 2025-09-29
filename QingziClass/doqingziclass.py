import copy

import SSPY.fuzzy.search as fuzzy_search
from SSPY.mypdf import PdfLoad
from SSPY.PersonneInformation import DefPerson
from SSPY.globalconstants import GlobalConstants as gc
from SSPY.myfolder import DefFolder
from SSPY.myxlsx import XlsxLoad, XlsxWrite


class DoQingziClass:
    """青字班程序控制库"""

    # def start(self):
    #     """仅向外提供此方法，以启动"""
    #     pass

    def __init__(self):
        self.__persons_all: list[DefPerson] = []  # """所有人员的名单"""
        self.__classname_all: list[str] = []  # 所有的班级名
        self.__unknownPersons: list[tuple[DefPerson, list[DefPerson]]] = []  # 未知的人员列表
        self.__load_person_all()

    def __self_check(self):
        """自检方法"""

    def __load_person_all(self):
        """加载所有的学员信息"""
        folder = DefFolder(gc.dir_INPUT_ALL_, extensions = ['.xlsx', '.XLSX'])
        self.__classname_all = folder.pure_filenames
        paths = folder.paths
        for p in paths:
            xlsx_sheet = XlsxLoad(p)  # 自动识别班级
            self.__persons_all.extend(xlsx_sheet.personList)


    def appSheet(self):
        def __load_person_app():
            """解析报集会名表中的人员"""
            folder = DefFolder(gc.dir_INPUT_APP_, extensions = ['.xlsx', '.XLSX'])
            paths = folder.paths
            classnames = folder.pure_filenames
            persons_app: list[DefPerson] = []
            for i in range(len(paths)):
                xlsx_sheet = XlsxLoad(paths[i])  # 自动识别班级
                persons_app.extend(xlsx_sheet.personList)
            return persons_app, classnames

        def __make_sheet(persons_app: list[DefPerson], classname: str) -> list[list[str]]:
            """制表"""
            for per_app in persons_app:
                per_all = self.search(per_app, push_unkown = False)
                if per_all is not None:
                    per_all.ifsign = True
            header = ['姓名', '学号']
            outSheet: list[list[str]] = [['序号', '姓名', '学号', '签到'], ]
            i = 1
            for per in self.__persons_all:
                if per.ifsign and per.classname == classname:
                    l: list[str] = [str(i)]
                    l.extend(per.to_list(header))
                    l.append('')
                    outSheet.append(l)
                    i += 1
            return outSheet

        def __save(sheet: list[list[str]], classname: str):
            writer = XlsxWrite(
                path = copy.copy(gc.dir_OUTPUT_APP_) + classname + '.xlsx',
                sheet = sheet,
                title = classname + '签到表',
                widths = [7, 24],
                height = 24,
                height_title = 40
            )
            writer.fontRegular = gc.fontRegularSong
            writer.fontTitle = gc.fontTitleGBK
            writer.border = gc.borderThinBlack
            if writer.can_write:
                writer.write()

        pers_app, cns = __load_person_app()
        for cn in cns:
            sh = __make_sheet(pers_app, cn)
            __save(sh, cn)


    def search(self, target: DefPerson, push_unkown = False) -> DefPerson | None:
        """从全部的库中搜索目标人员，返回总表人员的指针"""
        # up: tuple[DefPerson, list[DefPerson]]
        for per_a in self.__persons_all:
            if (per_a.classname == target.classname and
                    (self.is_same_studentID(target.studentID, per_a.studentID) or
                     target.name == per_a.name)):
                # 这里如果没有检测到学号，而只有学号，应该对名字进行全班判断，直到只有一个同名人才能返回
                return per_a
        if push_unkown:
            likely = []
            for per_a in self.__persons_all:
                if per_a.classname == target.classname:
                    if self.is_fuzzy_studentID(target.studentID, per_a.studentID):
                        likely.append(copy.deepcopy(per_a))
            if len(likely) > 0:
                self.__unknownPersons.append((copy.deepcopy(target), likely))
        return None

    @staticmethod
    def is_same_studentID(a: str, b: str) -> bool:
        if len(a) != len(b):  return False
        if len(a) < 4 or len(b) < 4: return False
        if a.endswith(('t', 'T')) and b.endswith(('t', 'T')):
            a_number_part = a[:-1]
            b_number_part = b[:-1]
            return a_number_part == b_number_part
        else:
            return a == b

    @staticmethod
    def is_fuzzy_studentID(a: str, b: str) -> bool:
        if len(a) < 4 or len(b) < 4: return False
        if a.endswith(('t', 'T')) and b.endswith(('t', 'T')):
            a_number_part = a[:-1]
            b_number_part = b[:-1]
            return fuzzy_search.match_by(a_number_part, b_number_part, fuzzy_search.LEVEL.High)
        else:
            return fuzzy_search.match_by(a, b, fuzzy_search.LEVEL.High)
