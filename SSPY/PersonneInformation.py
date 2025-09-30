import copy
from dis import name
from functools import singledispatchmethod
from .globalconstants import GlobalConstants as gc


class DefPerson:
    """表示一个人的结构体类，包含基本个人报名信息"""
    __keyWordTuple = {
        gc.chstrClassname         : (gc.chstrClassname, '班级名', '班级名字',
                                     '青字班', '青字班级', '青字班级名', '青字班级名字',
                                     '报名青字班', '报名班级'),
        gc.chstrName              : (gc.chstrName, '名字'),
        gc.chstrGrade             : (gc.chstrGrade, '所在年级'),
        gc.chstrStudentID         : (gc.chstrStudentID,),
        gc.chstrPoliticalOutlook  : (gc.chstrPoliticalOutlook,),
        gc.chstrAcademy           : (gc.chstrAcademy,),
        gc.chstrMajors            : (gc.chstrMajors,),
        gc.chstrPhone             : (gc.chstrPhone, '联系方式', '电话号码', '联系电话'),
        gc.chstrQQ                : (gc.chstrQQ, 'QQ', 'qq', 'qq号', 'Qq', 'qQ',
                                     'Qq号', 'qQ号', 'QQ号码', 'qq号码'),
        gc.chstrPosition          : (gc.chstrPosition, '担任职务', '当前职务', '所任岗位',
                                     '职务', '职位', '所任职位', '担任职位', '当前岗位'),
        gc.chstrEmail             : (gc.chstrEmail, '邮箱地址'),
        gc.chstrEthnicity         : (gc.chstrEthnicity,),
        gc.chstrClub              : (gc.chstrClub, '所在社团', '组织', '所在组织',
                                     '所属组织', '所属社团'),
        gc.chstrSignPosition      : (gc.chstrSignPosition, '报名职务', '报名位置'),
        gc.chstrGender            : (gc.chstrGender,),

        gc.chstrCheckIn           : (gc.chstrCheckIn,),
        gc.chstrNote              : (gc.chstrNote,),
        gc.chstrPersonalProfile   : (gc.chstrPersonalProfile,),
        gc.chstrPersonalExperience: (gc.chstrPersonalExperience,),
        gc.chstrPersonalStrengths : (gc.chstrPersonalStrengths,),
        gc.chstrWorkExperience    : (gc.chstrWorkExperience,),
        gc.chstrAwardsAndHonors   : (gc.chstrAwardsAndHonors,),
        gc.chstrMainAchievements  : (gc.chstrMainAchievements,),
    }

    def __init__(self,
                 cname: str = None,
                 name: str = None,
                 studentID: str = None) -> None:
        """
        Parameters
        ---------------
        cname : str
            班级名
        name :str
            姓名
        studentID : None
            学号
        """
        self.__classname: str
        self.__ifcheck = False
        self.__ifsign = False
        self.__information = {
            gc.chstrName            : '',
            gc.chstrGrade           : '',
            gc.chstrStudentID       : '',
            gc.chstrPoliticalOutlook: '',
            gc.chstrAcademy         : '',
            gc.chstrMajors          : '',
            gc.chstrPhone           : '',
            gc.chstrQQ              : '',
            gc.chstrPosition        : '',
            gc.chstrEmail           : '',
            gc.chstrEthnicity       : '',
            gc.chstrClub            : '',
            gc.chstrSignPosition    : ''}  # 信息
        if cname is not None: self.__classname = cname
        if name is not None: self.__information[gc.chstrName] = name
        if studentID is not None:
            self.__information[gc.chstrStudentID] = studentID

    def __str__(self) -> str:
        """适配print函数"""
        d = {'班级': self.__classname, }
        d.update(self.__information)
        d['ifsign'] = str(self.__ifsign)
        d['ifcheck'] = str(self.__ifcheck)
        return str(d)

    def __deepcopy__(self, memo: dict | None = None) -> 'DefPerson':
        """
        自定义深拷贝逻辑：确保拷贝对象与原对象独立
        :param memo: 缓存已拷贝对象，避免循环引用
        :return: DefPerson 深拷贝实例
        """
        # 1. 初始化memo（若未传入）
        if memo is None:
            memo = {}

        # 2. 检查当前实例是否已拷贝（避免循环引用重复拷贝）
        if id(self) in memo:
            return memo[id(self)]

        # 3. 深拷贝核心可变属性：__information（字典需递归拷贝）
        new_information = copy.deepcopy(self.__information, memo)

        # 4. 初始化新实例（不可变属性直接赋值，无需深拷贝）
        new_instance = DefPerson(
            cname = self.__classname,  # __classname是字符串（不可变）
            name = self.__information[gc.chstrName],  # 从原信息中取姓名（避免重复处理）
            studentID = self.__information[gc.chstrStudentID]  # 同理取学号
        )

        # 5. 补充赋值其他私有属性（__ifcheck、__ifsign是布尔值，不可变）
        new_instance.__ifcheck = self.__ifcheck
        new_instance.__ifsign = self.__ifsign
        # 覆盖__information：因为DefPerson.__init__会初始化空字典，需替换为深拷贝的字典
        new_instance.__information = new_information

        # 6. 将新实例存入memo，标记为已拷贝
        memo[id(self)] = new_instance

        return new_instance


    def optimize(self):
        """用于优化储存的信息"""
        if self.__information.get(gc.chstrEthnicity, '') != '':
            if not (self.__information[gc.chstrEthnicity].endswith('族')):
                self.__information[gc.chstrEthnicity] += '族'
        if self.__information.get(gc.chstrPoliticalOutlook, '') != '':
            if (self.__information[gc.chstrPoliticalOutlook] == '无'):
                self.__information[gc.chstrPoliticalOutlook] = '群众'
            elif ('团' in self.__information[gc.chstrPoliticalOutlook]):
                self.__information[gc.chstrPoliticalOutlook] = '共青团员'
            elif ('党' in self.__information[gc.chstrPoliticalOutlook]):
                if ('预' in self.__information[gc.chstrPoliticalOutlook]):
                    self.__information[gc.chstrPoliticalOutlook] = '中共预备党员'
                else:
                    self.__information[gc.chstrPoliticalOutlook] = '中共党员'
        if self.__information.get(gc.chstrStudentID, '') != '' and len(str(self.__information[gc.chstrStudentID])) > 4:
            first4 = self.__information[gc.chstrStudentID][:4]
            if first4.isdigit():
                if self.__information.get(gc.chstrGrade, '') != '':
                    if '研' in self.__information[gc.chstrGrade]:
                        self.__information[gc.chstrGrade] = '研' + first4 + '级'
                    else:
                        self.__information[gc.chstrGrade] = first4 + '级'
                else:
                    self.__information[gc.chstrGrade] = first4 + '级'
        if len(self.__classname) > 4:
            if '青' not in self.__classname or '班' not in self.__classname or '例' in self.__classname:
                for cn in gc.cns:
                    if cn[0] in self.__classname:
                        self.__classname = cn[1]
                # if gc.cXuan[0] in self.__classname:
                #     self.__classname = gc.cXuan[1]
                # elif gc.cWen[0] in self.__classname:
                #     self.__classname = gc.cWen[1]
                # elif gc.cGu[0] in self.__classname:
                #     self.__classname = gc.cGu[1]
                # elif gc.cXue[0] in self.__classname:
                #     self.__classname = gc.cXue[1]
                # elif gc.cYi[0] in self.__classname:
                #     self.__classname = gc.cYi[1]
                # elif gc.cFeng[0] in self.__classname:
                #     self.__classname = gc.cFeng[1]
                # elif gc.cGong[0] in self.__classname:
                #     self.__classname = gc.cGong[1]
                # elif gc.cShe[0] in self.__classname:
                #     self.__classname = gc.cShe[1]
                # elif gc.cShu[0] in self.__classname:
                #     self.__classname = gc.cShu[1]
                # elif gc.cYing[0] in self.__classname:
                #     self.__classname = gc.cYing[1]
                # elif gc.cZhi[0] in self.__classname:
                #     self.__classname = gc.cZhi[1]
                # elif gc.cZu[0] in self.__classname:
                #     self.__classname = gc.cZu[1]

    def set_information(self, inkey: str, value: str, if_fuzzy: bool = False):
        """添加信息"""
        if value == 'None': return
        key = self.get_stdkey(inkey, if_fuzzy)
        if key is None:
            self.__information[inkey] = value
        elif key == gc.chstrClassname:
            self.__classname = value
        else:
            self.__information[key] = value

    def get_information(self, inkey: str, if_fuzzy: bool = False) -> str:
        key = self.get_stdkey(inkey, if_fuzzy)
        if key is None:
            return self.__information.get(inkey, '')
        elif key == gc.chstrClassname:
            return self.__classname
        else:
            return self.__information.get(key, '')


    @staticmethod
    def get_stdkey(inkey: str, if_fuzzy: bool = False) -> str | None:
        """获取标准键"""
        for k in DefPerson.__keyWordTuple.keys():
            for item in DefPerson.__keyWordTuple[k]:
                if inkey == item:  # 采用字串检测
                    return k
        if if_fuzzy:
            for k in DefPerson.__keyWordTuple.keys():
                for item in DefPerson.__keyWordTuple[k]:
                    if item in inkey:
                        return k
            for k in DefPerson.__keyWordTuple.keys():
                for item in DefPerson.__keyWordTuple[k]:
                    if inkey in item:
                        return k
        return None

    @property
    def keyWordTuple(self):
        return copy.deepcopy(self.__keyWordTuple)

    @property
    def information(self):
        return copy.deepcopy(self.__information)

    @property
    def classname(self):
        return self.__classname

    @property
    def name(self):
        if self.__information.get(gc.chstrName, None) == None:
            self.__information[gc.chstrName] = ''
            return ''
        return self.__information[gc.chstrName]

    @property
    def grade(self):
        if self.__information.get(gc.chstrGrade, None) == None:
            self.__information[gc.chstrGrade] = ''
            return ''
        return self.__information[gc.chstrGrade]

    @property
    def studentID(self):
        if self.__information.get(gc.chstrStudentID, None) == None:
            self.__information[gc.chstrStudentID] = ''
            return ''
        return self.__information[gc.chstrStudentID]

    @property
    def politicalOutlook(self):
        if self.__information.get(gc.chstrPoliticalOutlook, None) == None:
            self.__information[gc.chstrPoliticalOutlook] = ''
            return ''
        return self.__information[gc.chstrPoliticalOutlook]

    @property
    def academy(self):
        if self.__information.get(gc.chstrAcademy, None) == None:
            self.__information[gc.chstrAcademy] = ''
            return ''
        return self.__information[gc.chstrAcademy]

    @property
    def majors(self):
        if self.__information.get(gc.chstrMajor, None) == None:
            self.__information[gc.chstrMajor] = ''
            return ''
        return self.__information[gc.chstrMajor]

    @property
    def phone(self):
        if self.__information.get(gc.chstrPhone, None) == None:
            self.__information[gc.chstrPhone] = ''
            return ''
        return self.__information[gc.chstrPhone]

    @property
    def qq(self):
        if self.__information.get(gc.chstrQQ, None) == None:
            self.__information[gc.chstrQQ] = ''
            return ''
        return self.__information[gc.chstrQQ]

    @property
    def position(self):
        if self.__information.get(gc.chstrPosition, None) == None:
            self.__information[gc.chstrPosition] = ''
            return ''
        return self.__information[gc.chstrPosition]

    @property
    def Email(self):
        if self.__information.get(gc.chstrEmail, None) == None:
            self.__information[gc.chstrEmail] = ''
            return ''
        return self.__information[gc.chstrEmail]

    @property
    def ethnicity(self):
        if self.__information.get(gc.chstrEthnicity, None) == None:
            self.__information[gc.chstrEthnicity] = ''
            return ''
        return self.__information[gc.chstrEthnicity]

    @property
    def club(self):
        if self.__information.get(gc.chstrClub, None) == None:
            self.__information[gc.chstrClub] = ''
            return ''
        return self.__information[gc.chstrClub]

    @property
    def signPosition(self):
        if self.__information.get(gc.chstrSignPosition, None) == None:
            self.__information[gc.chstrSignPosition] = ''
            return ''
        return self.__information[gc.chstrSignPosition]

    @property
    def gender(self):
        if self.__information.get(gc.chstrGender, None) == None:
            self.__information[gc.chstrGender] = ''
            return ''
        return self.__information[gc.chstrGender]

    @property
    def ifsign(self):
        return self.__ifsign

    @property
    def ifcheck(self):
        return self.__ifcheck

    @ifcheck.setter
    def ifcheck(self, value: bool):
        self.__ifcheck = value

    @ifsign.setter
    def ifsign(self, value: bool):
        self.__ifsign = value

    @classname.setter
    def classname(self, value: str):
        self.__classname = value

    @name.setter
    def name(self, value: str):
        self.__information[gc.chstrName] = value

    @grade.setter
    def grade(self, value: str):
        self.__information[gc.chstrGrade] = value

    @studentID.setter
    def studentID(self, value: str):
        self.__information[gc.chstrStudentID] = value

    @politicalOutlook.setter
    def politicalOutlook(self, value: str):
        self.__information[gc.chstrPoliticalOutlook] = value

    @academy.setter
    def academy(self, value: str):
        self.__information[gc.chstrAcademy] = value

    @majors.setter
    def majors(self, value: str):
        self.__information[gc.chstrMajor] = value

    @phone.setter
    def phone(self, value: str):
        self.__information[gc.chstrPhone] = value

    @qq.setter
    def qq(self, value: str | int):
        self.__information[gc.chstrQq] = str(value)

    @position.setter
    def position(self, value: str):
        self.__information[gc.chstrPosition] = str(value)

    @Email.setter
    def Email(self, value: str):
        self.__information[gc.chstrEmail] = str(value)

    @ethnicity.setter
    def ethnicity(self, value: str):
        self.__information[gc.chstrEthnicity] = str(value)

    @club.setter
    def club(self, value: str):
        self.__information[gc.chstrClub] = str(value)

    @signPosition.setter
    def signPosition(self, value: str):
        self.__information[gc.chstrSignPosition] = str(value)

    @gender.setter
    def gender(self, value: str):
        self.__information[gc.chstrGender] = str(value)

    def to_list(self, in_std: list[str]) -> list | None:
        """
        Parameters
        -------
        in_std : list[str]
            提取标准
        """
        outList = []
        for s in in_std:
            outList.append(self.get_information(s))
        return outList
