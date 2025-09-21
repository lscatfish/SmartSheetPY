from functools import singledispatchmethod
from pydoc import classname

from globalconstants import GlobalConstants as gc


class DefPerson:
    """表示一个人的结构体类，包含基本个人报名信息"""

    def __init__(self,
                 cname: str = None,
                 name: str = None,
                 studentID=None) -> None:
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
        self.classname: str
        self.ifcheck = False
        self.ifsign = True
        self.information = dict(((gc.chstrName, ''),
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
        if cname is not None: self.classname = cname
        if name is not None: self.information[gc.chstrName] = name
        if studentID is not None:
            if studentID is int:
                self.information[gc.chstrStudentID] = str(studentID)
            elif studentID is str:
                self.information[gc.chstrStudentID] = studentID

    def optimize(self):
        """用于优化储存的信息"""
        if self.information.get(gc.chstrEthnicity, '') != '':
            if not (self.information[gc.chstrEthnicity].endswith('族')):
                self.information[gc.chstrEthnicity] += '族'
        if self.information.get(gc.chstrPoliticalOutlook, '') != '':
            if (self.information[gc.chstrPoliticalOutlook] == '无'):
                self.information[gc.chstrPoliticalOutlook] = '群众'
            elif ('团' in self.information[gc.chstrPoliticalOutlook]):
                self.information[gc.chstrPoliticalOutlook] = '共青团员'
            elif ('党' in self.information[gc.chstrPoliticalOutlook]):
                if ('预' in self.information[gc.chstrPoliticalOutlook]):
                    self.information[gc.chstrPoliticalOutlook] = '中共预备党员'
                else:
                    self.information[gc.chstrPoliticalOutlook] = '中共党员'
        if self.information.get(gc.chstrStudentID, '') != '' and len(self.information[gc.chstrStudentID]) > 4:
            first4 = self.information[gc.chstrStudentID][:4]
            if first4.isdigit():
                if self.information.get(gc.chstrGrade, '') != '':
                    if '研' in self.information[gc.chstrGrade]:
                        self.information[gc.chstrGrade] = '研' + first4 + '级'
                    else:
                        self.information[gc.chstrGrade] = first4 + '级'
                else:
                    self.information[gc.chstrGrade] = first4 + '级'
        if len(classname) > 0:
