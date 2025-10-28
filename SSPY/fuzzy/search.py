# -*- coding: utf-8 -*-
"""模糊搜索模块"""
import copy
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


@unique
class Priority(Enum):
    """搜索优先级"""
    Time = 0
    """时间优先(最快)"""
    Similarity = 1
    """相似度优先"""


def match_by(a: str, b: str, level = LEVEL.Perfect):
    if isinstance(a, str) and isinstance(b, str):
        if level == LEVEL.Perfect:
            return a == b
        distance = levenshtein_distance(a, b)
        mp = level.value
        return distance <= mp
    return False


def searched_recursive(
    target: str,
    lib: tuple | list | str | dict,
    level = LEVEL.Perfect,
    target_as_sub: bool = False,
    lib_as_sub: bool = False):
    """
    对任意列表进行递归搜索，支持模糊
    Args:
        target:搜索目标
        lib:搜索的源
        level:搜索匹配度等级
        target_as_sub:将目标视作子串搜索
        lib_as_sub:将库字符视作子串搜索
    Returns:
        是否满足搜索条件
    """
    if target is None or target == '': return False
    if not isinstance(target, str): return False
    if isinstance(lib, list | tuple):
        for r in lib:
            if searched_recursive(target, r, level, target_as_sub, lib_as_sub):
                return True
    elif isinstance(lib, dict):
        for k in lib.keys():
            if searched_recursive(target, k, level, target_as_sub, lib_as_sub):
                return True
            if searched_recursive(target, lib[k], level, target_as_sub, lib_as_sub):
                return True
    elif isinstance(lib, str):
        if lib == '': return False
        if match_by(target, lib, level): return True
        if target_as_sub:
            if target in lib:
                return True
        if lib_as_sub:
            if lib in target:
                return True
    return False


def search_recursive(
    target: str,
    lib: tuple | list | str | dict,
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
        满足条件搜索值组成的一个列表
    """
    ms: list[str] = []
    if target is None: return ms
    if not isinstance(target, str): return ms
    if isinstance(lib, list | tuple):
        for r in lib:
            ms.extend(search_recursive(target, r, level, target_as_sub, lib_as_sub))
    elif isinstance(lib, dict):
        for k in lib.keys():
            ms.extend(search_recursive(target, k, level, target_as_sub, lib_as_sub))
            ms.extend(search_recursive(target, lib[k], level, target_as_sub, lib_as_sub))
    elif isinstance(lib, str):
        if match_by(target, lib, level): ms.append(lib)
        if target_as_sub:
            if target in lib: ms.append(lib)
        if lib_as_sub:
            if lib in target: ms.append(lib)
    return ms


def search_auto(
    target: str,
    lib: tuple | list | str,
    level = LEVEL.Perfect,
    target_as_sub: bool = False,
    lib_as_sub: bool = False, ):
    """
    基础函数，智能搜索函数
    Args:
        target:搜索目标
        lib:搜索的源
        level:搜索匹配度等级
        target_as_sub:将目标视作字串搜索
        lib_as_sub:将库字符视作字串搜索
    Returns:
        返回一个有序的结果
        排序规则：
        1.完全匹配
        2.target_as_sub
        3.lib_as_sub
        3.fuzzy
    """
    orgList = search_recursive(target, lib, level, target_as_sub, lib_as_sub)  # 解析出的原始序列

    if len(orgList) <= 1: return orgList

    sortedList: list[str] = []
    indices: list[int] = []

    def __del_by_indices():
        nonlocal indices
        nonlocal orgList
        if len(orgList) == 0 or len(indices) == 0: return
        for i in sorted(indices, reverse = True):
            del orgList[i]
        indices.clear()

    for index in range(len(orgList)):
        if match_by(target, orgList[index]):
            indices.append(index)
            sortedList.append(orgList[index])
    __del_by_indices()

    if target_as_sub:
        for index in range(len(orgList)):
            if target in orgList[index]:
                indices.append(index)
                sortedList.append(orgList[index])
        __del_by_indices()
    elif lib_as_sub:
        for index in range(len(orgList)):
            if orgList[index] in target:
                indices.append(index)
                sortedList.append(orgList[index])
        __del_by_indices()

    elif level != LEVEL.Perfect:
        dpMap: list[tuple[str, int]] = []
        for item in orgList:
            dpMap.append((item, levenshtein_distance(target, item)))
        sorteddpMap = sorted(dpMap, key = lambda x: x[1])
        for item in sorteddpMap:
            sortedList.append(item[0])
    return sortedList


def search_only(
    target: str,
    lib: tuple | list | str,
    level = LEVEL.Perfect,
    target_as_sub: bool = False,
    lib_as_sub: bool = False, ):
    """
    基础函数，智能搜索函数
    Args:
        target:搜索目标
        lib:搜索的源
        level:搜索匹配度等级
        target_as_sub:将目标视作字串搜索
        lib_as_sub:将库字符视作字串搜索
    Returns:
        返回最有可能的结果
        排序规则：
        1.完全匹配
        2.target_as_sub
        3.lib_as_sub
        3.fuzzy
    """
    inl = search_auto(target, lib, level, target_as_sub, lib_as_sub)
    if len(inl) == 0:
        return None
    else:
        return inl[0]
