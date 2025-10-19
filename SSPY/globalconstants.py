from openpyxl.styles import Font, Side, Border, Alignment


class GlobalConstants:
    """全局常量储存"""
    chstrQClassname = '青字班'
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
    chstrSignPosition = '应聘岗位'
    chstrGender = '性别'

    chstrRegistrationMethod = '报名方式'

    chstrNote = '备注'
    chstrCheckIn = '签到'
    chstrPersonalProfile = '个人简介'
    chstrPersonalExperience = '个人经历'
    chstrPersonalStrengths = '个人特长'
    chstrWorkExperience = '工作经历'
    chstrAwardsAndHonors = '获奖情况'
    chstrMainAchievements = '主要事迹'

    chstrFilePath = '文件地址'

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
    cKe = ('科', '青科班')

    cns = (cXuan, cWen, cGu, cXue, cYi, cFeng, cGong, cShe, cShu, cYing, cZhi, cZu, cKe)

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
    alignmentLeft = Alignment(vertical = 'center')

    dir_INPUT_ = '.\\input\\'
    dir_STORAGE_ = '.\\storage\\'
    dir_OUTPUT_ = '.\\output\\'

    dir_INPUT_ALL_ = '.\\input\\all\\'
    dir_INPUT_APP_ = '.\\input\\app\\'
    dir_INPUT_ATTIMGS_ = '.\\input\\att_imgs\\'
    dir_INPUT_SIGNFORQC_ = '.\\input\\sign_for_QingziClass\\'

    dir_OUTPUT_APP_ = '.\\output\\app_out\\'
    dir_OUTPUT_ATT_ = '.\\output\\att_out\\'
    dir_OUTPUT_SIGNFORQC_ = '.\\output\\sign_for_QingziClass_out\\'
    dir_OUTPUT_SIGNFORQC_unknown = '.\\output\\sign_for_QingziClass_out\\unknown\\'
    dir_OUTPUT_SIGNFORQC_committee = '.\\output\\sign_for_QingziClass_out\\committee\\'
    dir_OUTPUT_SIGNFORQC_classmate = '.\\output\\sign_for_QingziClass_out\\classmate\\'
    dir_OUTPUT_SIGNFORQC_classmate_unc = '.\\output\\sign_for_QingziClass_out\\classmate\\unknown_class\\'

    dir_MODEL_NATURE_ = '.\\official_models\\'

    dirs_need = (
        dir_INPUT_,
        dir_STORAGE_,
        dir_OUTPUT_,
        dir_INPUT_ALL_,
        dir_INPUT_APP_,
        dir_INPUT_ATTIMGS_,
        dir_INPUT_SIGNFORQC_,
        dir_OUTPUT_APP_,
        dir_OUTPUT_ATT_,
        dir_OUTPUT_SIGNFORQC_,
        dir_OUTPUT_SIGNFORQC_unknown,
        dir_OUTPUT_SIGNFORQC_committee,
        dir_OUTPUT_SIGNFORQC_classmate,
        dir_OUTPUT_SIGNFORQC_classmate_unc,
        dir_MODEL_NATURE_,
    )

    extensions_XLSX = ['.xlsx', '.XLSX']
    extensions_DOCX = ['.docx', '.DOCX']
    extensions_PDF = ['.pdf', '.PDF']
    extensions_IMG = [".jpg", ".png", ".jpeg", ".tiff", ".tif ",
                      ".jpe", ".bmp", ".dib", ".webp", ".raw"]

    @staticmethod
    def get_classname_from_path(path: str):
        """从path中获取班级名"""
        import re
        match = re.search(r'青([\u4e00-\u9fa5])班', path)
        if match:
            for cn in GlobalConstants.cns:
                if cn[0] == match.group(1):
                    return cn[1]
        for cn in GlobalConstants.cns:
            if cn[0] in path:
                return cn[1]
        raise Exception(f'文件{path}命名错误，请包含关键词')  # 未找到匹配的结构

    @staticmethod
    def create_folders_must():
        """创建必要文件夹"""
        from .myfolder import create_nested_folders
        for d in GlobalConstants.dirs_need:
            create_nested_folders(d)


    def __setattr__(self, name, value):
        raise AttributeError("Can't set attribute")
