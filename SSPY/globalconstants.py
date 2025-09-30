from openpyxl.styles import Font, Side, Border, Alignment


class GlobalConstants:
    """全局常量储存"""
    chstrClassname = '班级'
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

    chstrNote = '备注'
    chstrCheckIn = '签到'
    chstrPersonalProfile = '个人简介'
    chstrPersonalExperience = '个人经历'
    chstrPersonalStrengths = '个人特长'
    chstrWorkExperience = '工作经历'
    chstrAwardsAndHonors = '获奖情况'
    chstrMainAchievements = '主要事迹'

    cXuan = ('宣', '青宣班')
    cWen = ('文', '青文班')
    cGu = ('骨', '青骨班')
    cXue = ('学', '青学班')
    cYi = ('艺', '青艺班')
    cFeng = ('峰', '青峰班')
    cGong = ('公', '青公班')
    cShe = ('社', '青社班')
    cShu = ('书', '青书班')
    cYing = ('膺', '青膺班')
    cZhi = ('志', '青志班')
    cZu = ('组', '青组班')

    cns = (cXuan, cWen, cGu, cXue, cYi, cFeng, cGong, cShe, cShu, cYing, cZhi, cZu)

    fontRegularGBK = Font(name = '仿宋_GB2312', size = 14)
    fontRegularSong = Font(name = '宋体', size = 14)
    fontRegularSongSmall = Font(name = '宋体', size = 10)
    fontTitleGBK = Font(name = '宋体', size = 24, bold = True)
    fontHeaderGBK = Font(name = '仿宋_GB2312', size = 14, bold = True)
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

    dir_INPUT_ = '.\\input\\'
    dir_STORAGE_ = '.\\storage\\'
    dir_OUTPUT_ = '.\\output\\'

    dir_INPUT_ALL_ = '.\\input\\all\\'
    dir_INPUT_APP_ = '.\\input\\app\\'
    dir_INPUT_ATTIMGS_ = '.\\input\\att_imgs\\'
    dir_INPUT_SIGNFORQC_ = '.\\input\\sign_for_QingziClass\\'

    dir_OUTPUT_APP_ = '.\\output\\app_out\\'
    dir_OUTPUT_ATT = '.\\output\\att_out\\'
    dir_OUTPUT_SIGNFORQC_ = '.\\output\\sign_for_QingziClass_out\\'

    extensions_XLSX = ['.xlsx', '.XLSX']
    extensions_DOCX = ['.docx', '.DOCX']
    extensions_IMG = [".jpg", ".png", ".jpeg", ".tiff", ".tif ",
                      ".jpe", ".bmp", ".dib", ".webp", ".raw"]

    def __setattr__(self, name, value):
        raise AttributeError("Can't set attribute")
