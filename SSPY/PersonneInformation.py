import copy
import os.path
from dis import name
from functools import singledispatchmethod
from .globalconstants import GlobalConstants as gc
import types


class DefPerson:
    """表示一个人的结构体类，包含基本个人报名信息"""
    __raw_key_word = {
        gc.chstrQClassname        : (gc.chstrQClassname, '班级名', '班级名字',
                                     '青字班', '青字班级', '青字班级名', '青字班级名字',
                                     '报名青字班', '报名班级', '班级'),
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
        gc.chstrSignPosition      : (gc.chstrSignPosition, '报名职务', '报名位置', '报名岗位'),
        gc.chstrGender            : (gc.chstrGender,),

        gc.chstrRegistrationMethod: (gc.chstrRegistrationMethod,),
        gc.chstrCheckIn           : (gc.chstrCheckIn,),
        gc.chstrNote              : (gc.chstrNote,),
        gc.chstrPersonalProfile   : (gc.chstrPersonalProfile,),
        gc.chstrPersonalExperience: (gc.chstrPersonalExperience,),
        gc.chstrPersonalStrengths : (gc.chstrPersonalStrengths,),
        gc.chstrWorkExperience    : (gc.chstrWorkExperience,),
        gc.chstrAwardsAndHonors   : (gc.chstrAwardsAndHonors,),
        gc.chstrMainAchievements  : (gc.chstrMainAchievements,),
        gc.chstrFilePath          : (gc.chstrFilePath, '地址', '文件路径', '路径', 'path')
    }
    __keyWordTuple = types.MappingProxyType(__raw_key_word)

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
        self.__classname: str = ''
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
        self.__filepaths: list[str] = []  # 此人员相关的文件路径
        """从哪里来"""
        self.__savepaths: list[str] = []  # 保存的文件路径
        """到哪里去"""
        if cname is not None: self.__classname = cname
        if name is not None: self.__information[gc.chstrName] = name
        if studentID is not None:
            self.__information[gc.chstrStudentID] = studentID

    def __str__(self) -> str:
        """适配print函数"""
        d = {gc.chstrQClassname: self.__classname, }
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
        new_instance.__filepaths = copy.deepcopy(self.__filepaths)

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
        if len(self.__classname) > 0:
            orgcn = self.__classname
            """原始名称"""
            self.__classname = ''
            for cn in gc.cns:
                if cn[0] in orgcn:
                    if self.__classname != '':
                        self.__classname += (',' + cn[1])
                        continue
                    self.__classname += cn[1]
            if self.__classname == '':
                self.__classname = orgcn


    def set_information(
        self,
        inkey: str,
        value: str | list[str],
        inkey_as_sub: bool = False,
        stdkey_as_sub: bool = False):
        """添加信息"""
        if str(value) == 'None': return
        key = self.get_stdkey(inkey, inkey_as_sub = inkey_as_sub, stdkey_as_sub = stdkey_as_sub)
        if key is None:
            self.__information[inkey] = value
        elif key == gc.chstrQClassname:
            self.__classname = value
        elif key == gc.chstrFilePath:
            self.filepath = value
        else:
            self.__information[key] = value

    def get_information(
        self, inkey: str,
        inkey_as_sub: bool = False,
        stdkey_as_sub: bool = False,
        return_str = True) -> str | list[str]:
        """
        查找一个键，无论这个键是否存在都返回空字符
        Args:
            inkey:查找的键
            inkey_as_sub:输入的键作为子串
            stdkey_as_sub:标准键作为字串
            return_str:只返回str
        """
        from .helperfunction import trans_list_to_str
        if self.__information.get(inkey, None) is None:
            key = self.get_stdkey(inkey, inkey_as_sub = inkey_as_sub, stdkey_as_sub = stdkey_as_sub)
            if key is None:
                return self.__information.get(inkey, '')
            elif key == gc.chstrQClassname:
                return self.__classname
            elif key == gc.chstrFilePath:
                if return_str:
                    return trans_list_to_str(self.__filepaths)
                return self.filepath
            else:
                return self.__information.get(key, '')
        else:
            return self.__information.get(inkey, '')


    @staticmethod
    def get_stdkey(
        inkey: str,
        inkey_as_sub: bool = False,
        stdkey_as_sub: bool = False) -> str | None:
        """
        获取标准键，
        一般来说应该将输入键作为字串
        Args:
            inkey:查找的键
            inkey_as_sub:查找键作为字串匹配
            stdkey_as_sub:标准键作为字串匹配
        Returns:
            标准键参数
        """
        if inkey is None or inkey == '': return None
        for k in DefPerson.__keyWordTuple.keys():
            for item in DefPerson.__keyWordTuple[k]:
                if inkey == item:  # 采用字串检测
                    return k
        if inkey_as_sub:
            for k in DefPerson.__keyWordTuple.keys():
                for item in DefPerson.__keyWordTuple[k]:
                    if inkey in item:
                        return k
        if stdkey_as_sub:
            for k in DefPerson.__keyWordTuple.keys():
                for item in DefPerson.__keyWordTuple[k]:
                    if item in inkey:
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

    @property
    def filepath(self):
        """文件的相关路径"""
        return copy.deepcopy(self.__filepaths)

    @property
    def savepath(self):
        """保存文件的路径"""
        return copy.deepcopy(self.__savepaths)

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

    @filepath.setter
    def filepath(self, value: str | list[str]):
        """补充文件路径（从哪里来）"""
        if isinstance(value, str):
            self.__filepaths.append(value)
        elif isinstance(value, list):
            self.__filepaths.extend(copy.deepcopy(value))
        else:
            raise Exception('filepath 只能接受 str 与 list[str] 格式！！！')

    @savepath.setter
    def savepath(self, value: str | list[str]):
        """补充保存路径"""
        if isinstance(value, str):
            self.__savepaths.append(value)
        elif isinstance(value, list):
            self.__savepaths.extend(copy.deepcopy(value))
        else:
            raise Exception('savepath 只能接受 str 与 list[str] 格式！！！')

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

    def merge(self, other: 'DefPerson'):
        """合并other的信息到this"""
        self.__ifsign = (other.ifsign or self.__ifsign)
        self.__ifcheck = (other.ifcheck or self.__ifcheck)
        oinfo = other.information
        for key in oinfo:
            self_key_value = self.get_information(key)
            if self_key_value != '' and self_key_value != 'None' and self_key_value != '-':
                continue
            else:  # 为空
                self.__information[key] = oinfo[key]
                continue
        self.__classname += other.classname
        self.__filepaths.extend(copy.deepcopy(other.__filepaths))
        self.__filepaths = list(dict.fromkeys(self.__filepaths))  # 键去重方法

    def gen_classes(self):
        """产生班级列表"""
        clss = (gc.generate_class_list(self.__classname) +
                gc.generate_class_list(self.get_information(gc.chstrSignPosition)))
        if len(clss) == 0:
            clss.append('unknown_class')
        return clss

    def copy_files(
        self,
        main_root = gc.dir_OUTPUT_SIGNFORQC_classmate,
        under_class_folder = True,
        gen_solofolder = True,
        keep_origin_name = False, ):
        """
        复制文件
        Args:
            main_root :目标文件母目录
            under_class_folder:是否要放在对应的青字班文件夹下
            gen_solofolder:是否生成单独的一个文件夹
            keep_origin_name :是否保持原名称
        """
        from .myfolder import (
            create_nested_folders,
            copy_file,
            get_filename_with_extension,
            split_filename_and_extension,
            get_top_parent_dir_by,
            parent_dir)
        from shutil import copytree
        sum = 0
        target_: list[str] = []
        if len(self.__filepaths) == 0: return sum
        if under_class_folder:
            classnames = self.gen_classes()
            for i in range(len(classnames)):
                target_.append(main_root + '/' + classnames[i] + '/')
        if gen_solofolder:
            for i in range(len(target_)):
                target_[i] = (target_[i] + self.get_information('报名方式') + '-'
                              + self.name + '-' + self.studentID + '/')
        # 生成文件夹
        for tr in target_: create_nested_folders(tr, if_print = False)
        # 复制文件
        for fp in self.__filepaths:
            for tr in target_:
                t = ((tr + get_filename_with_extension(fp)) if keep_origin_name
                     else (tr + self.name + '-' + self.studentID + split_filename_and_extension(fp)[1]))
                j = 0
                while os.path.exists(t):
                    j += 1
                    a, b = split_filename_and_extension(fp)
                    t = ((tr + a + f'({j})' + b) if keep_origin_name
                         else (tr + self.name + '-' + self.studentID + f'({j})' + b))
                    if j > 20: break
                copy_file(fp, t, True)
                self.savepath = t
                sum += 1

        # 获取关联文件
        dirs = get_top_parent_dir_by(gc.dir_INPUT_SIGNFORQC_, self.__filepaths[0])
        if os.path.isdir(dirs):
            print(dirs)
            print(parent_dir(self.__savepaths[0])[0] + f"/原始文件/{os.path.basename(dirs)}")
            copytree(dirs,
                parent_dir(self.__savepaths[0])[0] + f"/原始文件/{os.path.basename(dirs)}", dirs_exist_ok = True)
        return sum


def is_studentID(s: str):
    import re
    # 1. 检查是否只包含数字和英文（排除所有其他字符，包括汉字）
    # 正则说明：^ 匹配开头，$ 匹配结尾，[0-9a-zA-Z] 匹配数字和英文，+ 表示至少1个字符
    if not re.fullmatch(r'^[0-9a-zA-Z]+$', s):
        return False  # 包含非数字/英文的字符（如汉字、符号、空格等）

    # 2. 提取纯数字部分（排除最后一位可能的字母）
    # 匹配规则：前面全是数字，最后一位可以是数字或字母
    match = re.fullmatch(r'(\d+)([a-zA-Z]?)', s)
    if not match:
        return False  # 不符合“数字+可选字母结尾”的结构（如字母在开头）

    # 3. 检查数字部分长度是否 >6（即至少7位）
    digits_part = match.group(1)  # 数字部分（不含末尾字母）
    return len(digits_part) >= 6
