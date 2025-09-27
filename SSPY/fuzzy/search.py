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
    Unknow = 1000


def match_by(a: str, b: str, level = LEVEL.Perfect):
    if level == LEVEL.Perfect:
        return a == b
    distance = levenshtein_distance(a, b)
    mp = level.value
    return distance <= mp


def search_in(target: str, lib: list, level = LEVEL.Perfect):
    """返回搜索到的表"""
    out_list = []
    for a in lib:
        if match_by(target, a, level):
            out_list.append(a)
    return out_list


def searched(target: str, lib: list, level = LEVEL.Perfect) -> bool:
    """返回是否搜索到"""
    for a in lib:
        if match_by(target, a, level):
            return True
    return False
