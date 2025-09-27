from SSPY.mypdf import PdfLoad
from SSPY.PersonneInformation import DefPerson
from SSPY.globalconstants import GlobalConstants as gc
from SSPY.myfolder import DefFolder


class DoQingziClass:
    """青字班程序控制库"""

    # def start(self):
    #     """仅向外提供此方法，以启动"""
    #     pass

    def __init__(self):
        self.__person_all = []  # """所有人员的名单"""
        self.__classname_all = []  # 所有的班级名
        pass

    def __self_check(self):
        """自检方法"""

    def __load_person_all(self):
        """加载所有的学员信息"""
        folder = DefFolder(gc.dir_INPUT_ALL_)
        self.__classname_all = folder.get_pure_filenames_by(['.xlsx', '.XLSX'])
        files = folder.get_paths_by(['.xlsx', '.XLSX'])


print()
