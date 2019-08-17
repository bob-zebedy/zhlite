# -*- coding: utf-8 -*-

from zhlite.zhlite import *

__author__ = "zhangbo"
__email__ = "deplives@deplives.com"

__license__ = "MIT"

__version__ = "1.3.2"
__date__ = "2019-08-17"
__release__ = "增加请求随机(0s~1s)间隔 尽可能减少账号因为请求频繁被要求输入验证码"


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

__all__ = ["Authorization", "User", "Question", "Answer"]
