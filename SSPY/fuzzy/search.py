"""模糊搜索模块"""
from enum import Enum, unique


def levenshtein_distance(s: str, t: str) -> int:
    """
    计算两个字符串之间的Levenshtein距离（编辑距离）
    即通过插入、删除、替换操作将s转换为t所需的最少操作次数

    Parameters:
        s: 源字符串
        t: 目标字符串

    Returns:
        两个字符串的编辑距离
    """
    m = len(s)
    n = len(t)

    # 创建(m+1)x(n+1)的二维数组，初始化所有元素为0
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    # 初始化边界条件
    for i in range(m + 1):
        dp[i][0] = i  # 第一列：将s的前i个字符删除变为空字符串
    for j in range(n + 1):
        dp[0][j] = j  # 第一行：从空字符串插入j个字符变为t

    # 填充DP表
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            # 计算替换成本：字符相同则成本为0，否则为1
            cost = 0 if s[i - 1] == t[j - 1] else 1

            # 取三种操作的最小值：删除、插入、替换
            dp[i][j] = min(
                dp[i - 1][j] + 1,  # 删除操作：删除s[i-1]
                dp[i][j - 1] + 1,  # 插入操作：插入t[j-1]到s
                dp[i - 1][j - 1] + cost  # 替换操作：将s[i-1]替换为t[j-1]
            )

    return dp[m][n]


@unique
class LEVEL(Enum):
    """匹配度"""
    Perfect = 0
    High = 1
    Medium = 2
    Low = 3
    L4 = 4
    L5 = 5
    L6 = 6
    L7 = 7
    L8 = 8
    L9 = 9
    L10 = 10
    L11 = 11
    L12 = 12
    L13 = 13
    Unknow = 1000


def match_by(a: str, b: str, level = LEVEL.Perfect):
    if level == LEVEL.Perfect:
        return a == b
    distance = levenshtein_distance(a, b)
    mp = level.value
    return distance <= mp


def search_in(target: str, lib: list[str], level = LEVEL.Perfect):
    """返回搜索到的表"""
    out_list = []
    for a in lib:
        if match_by(target, a, level):
            out_list.append(a)
    return out_list


def searched(target: str, lib: list[str], level = LEVEL.Perfect) -> bool:
    """返回是否搜索到"""
    for a in lib:
        if match_by(target, a, level):
            return True
    return False


def searched_auto(
    target: str,
    lib: tuple | list | str,
    level = LEVEL.Perfect,
    target_as_sub: bool = False,
    lib_as_sub: bool = False):
    """
    对任意列表进行递归搜索，支持模糊
    Args:
        target:搜索目标
        lib:搜索的源
        level:搜索匹配度等级
        target_as_sub:将目标视作字串搜索
        lib_as_sub:将库字符视作字串搜索
    Returns:
        是否满足搜索条件
    """
    if target is None: return False
    if not isinstance(target, str): return False
    if isinstance(lib, list | tuple):
        for r in lib:
            if searched_auto(target, r, level, target_as_sub, lib_as_sub):
                return True
    elif isinstance(lib, str):
        if match_by(target, lib, level):
            return True
        if target_as_sub:
            if target in lib: return True
        if lib_as_sub:
            if lib in target: return True
    return False
