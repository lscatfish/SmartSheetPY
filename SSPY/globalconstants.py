class GlobalConstants:
    chstrName = '姓名'
    chstrGrade = '年级'
    chstrStudentID = '学号'
    chstrPoliticalOutlook = '政治面貌'
    chstrAcademy = '学院'
    chstrMajors = '专业'
    chstrPhone = '电话'
    chstrQQ = 'QQ号'
    chstrPosition = '所任职务'
    chstrEmail = '邮箱'
    chstrEthnicity = '民族'
    chstrClub = '社团'
    chstrSignPosition = '报名岗位'
    chstrGender = '性别'

    def __setattr__(self, name, value):
        raise AttributeError("Can't set attribute")
