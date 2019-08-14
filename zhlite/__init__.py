# -*- coding: utf-8 -*-

from zhlite.zhlite import *

__author__ = "zhangbo"
__email__ = "deplives@deplives.com"

__license__ = "MIT"

__version__ = "1.3.0"
__date__ = "2019-08-14"
__release__ = "新增 ZhliteBase 作为基础父类，其余模块均继承该父类。抽象公共代码"


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

__all__ = ["Oauth", "User", "Question", "Answer"]
