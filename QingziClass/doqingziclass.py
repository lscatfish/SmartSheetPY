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
        folder = DefFolder(gc.dir_INPUT_ALL_, extensions = gc.extensions_XLSX)
        self.__classname_all = folder.pure_filenames
        paths = folder.paths
        for p in paths:
            xlsx_sheet = XlsxLoad(p)  # 自动识别班级
            self.__persons_all.extend(xlsx_sheet.get_personList())


    def appSheet(self):
        """签到表"""

        def __load_person_app():
            """解析报集会名表中的人员"""
            folder = DefFolder(gc.dir_INPUT_APP_, extensions = ['.xlsx', '.XLSX'])
            paths = folder.paths
            classnames = folder.pure_filenames
            persons_app: list[DefPerson] = []
            for i in range(len(paths)):
                xlsx_sheet = XlsxLoad(paths[i])  # 自动识别班级
                persons_app.extend(xlsx_sheet.get_personList())
            return persons_app, classnames

        def __person_sign(persons_app: list[DefPerson]):
            """标记人员"""
            for per_app in persons_app:
                per_all = self.search(per_app, push_unknown = True)
                if per_all is not None:
                    per_all.ifsign = True

        def __make_sheet(classname: str) -> list[list[str]]:
            """制表"""
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

        def __storage():
            """储存报名信息"""
            sheet: list[list[str]] = []
            header = [gc.chstrClassname, gc.chstrName, gc.chstrStudentID]
            sheet.append(header)
            for per in self.__persons_all:
                if per.ifsign:
                    sheet.append(per.to_list(header))
            XlsxWrite(
                path = copy.copy(gc.dir_STORAGE_) + 'storage.xlsx',
                sheet = sheet,
                font_regular = gc.fontRegularSongSmall
            ).write()

        pers_app, cns = __load_person_app()
        __person_sign(pers_app)
        for cn in cns:
            sh = __make_sheet(cn)
            __save(sh, cn)
        __storage()
        self.__unknownSheet()

    def attSheet(self):

        def __organize_imgs() -> dict[str, list[str]]:
            """整理照片以及其地址"""
            classname_imgpath: dict[str, list[str]] = {}
            folder = DefFolder(gc.dir_INPUT_ATTIMGS_, extensions = gc.extensions_IMG)
            for p in folder.paths:
                for cn in gc.cns:
                    if cn[0] in p:
                        if classname_imgpath.get(cn[1], '') == '':
                            classname_imgpath[cn[1]] = [p, ]
                        else:
                            classname_imgpath[cn[1]].append(p)
            # print(classname_imgpath)
            return classname_imgpath

        def __parse_imgs(cn_ip: dict[str, list[str]]) -> list[DefPerson]:
            persons_att: list[DefPerson] = []
            # 启用ocr
            from SSPY.myimg import PPOCRImgByModel
            ocr = PPOCRImgByModel()
            for cn in cn_ip.keys():
                for ip in cn_ip[cn]:
                    ocr.predict(ip)
                persons_att.extend(ocr.get_personList(cn, ifp = True))
            return persons_att

        def __person_checkin(persons_att: list[DefPerson]):
            """检查是否签到"""
            for per_att in persons_att:
                per_all = self.search(per_att, push_unknown = True)
                if per_all is not None:
                    qd = per_all.get_information('签到')
                    if qd != '' and qd != 'None':
                        per_all.ifcheck = True

        def __make_sheet(classname: str) -> list[list[str]]:
            """制表"""
            in_header = [gc.chstrName, gc.chstrStudentID, gc.chstrAcademy, '联系方式']
            out: list[list[str]] = [
                [gc.chstrName, gc.chstrStudentID, gc.chstrAcademy, '联系方式', gc.chstrCheckIn, '备注'], ]
            for per in self.__persons_all:
                if per.classname == classname:
                    l = per.to_list(in_header)
                    if per.ifcheck:
                        l.append('已签到')
                    else:
                        l.append('')
                    if per.ifsign:
                        l.append('')
                    else:
                        l.append('未报名')
                    out.append(l)
            return out

        def __save(sheet: list[list[str]], classname: str):
            """保存签到表"""
            from openpyxl.styles import Font, Border, Alignment
            writer = XlsxWrite(
                path = copy.copy(gc.dir_OUTPUT_ATT) + classname + '线下签到汇总表.xlsx',
                sheet = sheet,
                widths = [40, 40],
                height = 25,
                font_regular = Font(name = '宋体', size = 16)
            )
            writer.heightTitle = 45
            writer.title = classname + '线下签到汇总表'
            writer.fontTitle = Font(name = '方正小标宋简体', size = 26)
            writer.border = gc.borderThinBlack
            writer.write()

        self.__load_storage()
        pers_att = __parse_imgs(__organize_imgs())
        __person_checkin(pers_att)
        for cn in self.__classname_all:
            __save(__make_sheet(cn), cn)
        self.__unknownSheet()


    def __load_storage(self):
        """加载临时文件，自动报名"""
        pers_app = XlsxLoad(
            _path = gc.dir_STORAGE_ + 'storage.xlsx',
            const_classname = False,
        ).get_personList()
        for p_app in pers_app:
            for per in self.__persons_all:
                if per.classname == p_app.classname and self.is_same_studentID(per.studentID, p_app.studentID):
                    per.ifsign = True

    def __unknownSheet(self):
        sheet: list[list[str]] = [['类型', gc.chstrClassname, gc.chstrName, gc.chstrStudentID], ]
        header = [gc.chstrClassname, gc.chstrName, gc.chstrStudentID]
        if len(self.__unknownPersons) > 0:
            for per in self.__unknownPersons:
                # print(per[0])
                l: list[str] = ['*UNKNOWN', ]
                l.extend(per[0].to_list(header))
                sheet.append(l)
                for lp in per[1]:
                    l2: list[str] = ['-LIKELY', ]
                    l2.extend(lp.to_list(header))
                    sheet.append(l2)
            for r in sheet:
                for cell in r:
                    print(cell, end = '\t')
                print(end = '\n')
        else:
            print('没有未知人员')
        XlsxWrite(
            path = copy.copy(gc.dir_OUTPUT_) + 'unknown.xlsx',
            sheet = sheet,
            font_regular = gc.fontRegularSongSmall,
            widths = [24, ]
        ).write()

    def search(self, target: DefPerson, push_unknown = False) -> DefPerson | None:
        """从全部的库中搜索目标人员，返回总表人员的指针"""
        same_name = 0
        for per_a in self.__persons_all:
            if per_a.classname == target.classname:
                if self.is_same_studentID(target.studentID, per_a.studentID):
                    return per_a
                elif target.name == per_a.name:
                    maybe_per = per_a
                    same_name += 1
        if same_name == 1:
            return maybe_per
        if push_unknown:
            likely: list[DefPerson] = []
            for per_a in self.__persons_all:
                if per_a.classname == target.classname:
                    if self.is_fuzzy_studentID(target.studentID, per_a.studentID):
                        likely.append(copy.deepcopy(per_a))
                    elif fuzzy_search.match_by(per_a.name, target.name, fuzzy_search.LEVEL.High):
                        likely.append(copy.deepcopy(per_a))
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
