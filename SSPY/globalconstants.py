from openpyxl.styles import Font, Side, Border, Alignment


class GlobalConstants:
    """全局常量储存"""
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
    fontRegularGBK = Font(name = '仿宋_GB2312', size = 14)
    borderThinBlack = Border(
        left = Side(style = "thin", color = "000000"),
        right = Side(style = "thin", color = "000000"),
        top = Side(style = "thin", color = "000000"),
        bottom = Side(style = "thin", color = "000000")
    )
    """定义边框样式：细实线、黑色"""
    borderThickBlack = Border(
        left = Side(style = "thick", color = "0000FF"),
        right = Side(style = "thick", color = "0000FF"),
        top = Side(style = "thick", color = "0000FF"),
        bottom = Side(style = "thick", color = "0000FF")
    )
    """定义粗边框样式：粗实线、蓝色"""
    alignmentStd = Alignment(horizontal = 'center', vertical = 'center')
    """标准对齐方式"""

    def __setattr__(self, name, value):
        raise AttributeError("Can't set attribute")
