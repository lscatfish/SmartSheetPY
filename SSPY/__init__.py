# -*- coding: utf-8 -*-
"""
every package is doomed to be shit

如果你单独使用此包，我们推荐你劫持ppocr的下载器以及相关子线程
If you use this package alone, we recommend that you hijack the ppocr downloader and the related subthreads.

@attention 此包并没有适配任何线程安全的功能，若启用多线程，在使用ppocr的时候应当注意线程安全

"""

__version__ = '0.6.7'
from .communitor.core import register_communitor as register_SSPY_communitor
