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
                 studentID = str) -> None:
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
        self.__information = dict(
            ((gc.chstrName, ''),
             (gc.chstrGrade, ''),
             (gc.chstrStudentID, ''),
             (gc.chstrPoliticalOutlook, ''),
             (gc.chstrAcademy, ''),
             (gc.chstrMajors, ''),
             (gc.chstrPhone, ''),
             (gc.chstrQQ, ''),
             (gc.chstrPosition, ''),
             (gc.chstrEmail, ''),
             (gc.chstrEthnicity, ''),
             (gc.chstrClub, ''),
             (gc.chstrSignPosition, '')))  # 信息
        if cname is not None: self.__classname = cname
        if name is not None: self.__information[gc.chstrName] = name
        if studentID is not None:
            self.__information[gc.chstrStudentID] = studentID

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
        if self.__information.get(gc.chstrStudentID, '') != '' and len(self.__information[gc.chstrStudentID]) > 4:
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
                if '宣' in self.__classname:
                    self.__classname = '青宣班'
                elif '文' in self.__classname:
                    self.__classname = '青文班'
                elif '骨' in self.__classname:
                    self.__classname = '青骨班'
                elif '学' in self.__classname:
                    self.__classname = '青学班'
                elif '艺' in self.__classname:
                    self.__classname = '青艺班'
                elif '峰' in self.__classname:
                    self.__classname = '青峰班'
                elif '公' in self.__classname:
                    self.__classname = '青公班'
                elif '社' in self.__classname:
                    self.__classname = '青社班'
                elif '书' in self.__classname:
                    self.__classname = '青书班'
                elif '膺' in self.__classname:
                    self.__classname = '青膺班'
                elif '志' in self.__classname:
                    self.__classname = '青志班'
                elif '组' in self.__classname:
                    self.__classname = '青组班'

    def set_information(self, inkey: str, value: str):
        """添加信息"""
        key = self.get_stdkey(inkey)
        if key is None:
            self.__information[inkey] = value
        elif key == gc.chstrClassname:
            self.__classname = value
        else:
            self.__information[key] = value

    def get_information(self, inkey: str) -> str:
        key = self.get_stdkey(inkey)
        if key is None:
            return self.__information.get(inkey, '')
        elif key == gc.chstrClassname:
            return self.__classname
        else:
            return self.__information.get(key, '')


    @staticmethod
    def get_stdkey(inkey: str) -> str | None:
        """获取标准键"""
        for k in DefPerson.__keyWordTuple.keys():
            for item in DefPerson.__keyWordTuple[k]:
                if inkey == item:  # 采用字串检测
                    return k
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
