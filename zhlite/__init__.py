# -*- coding: utf-8 -*-

from zhlite.zhlite import *

__author__ = "zhangbo"
__email__ = "deplives@deplives.com"

__license__ = "MIT"

__version__ = "1.6.5"
__date__ = "2019-09-01"
__release__ = "请求超时设置为 10s"


class Version(object):

    def __init__(self):
        self.info = {
            "version": __version__,
            "date": __date__,
            "release": __release__
        }

    def __str__(self):
        return " ".join([f"{k}: {v}" for k, v in self.info.items()])


version = Version()

__all__ = ["Auth", "User", "Question", "Answer", "Article"]
