# -*- coding: utf-8 -*-

from zhlite.zhlite import *

__author__ = "zhangbo"
__email__ = "deplives@deplives.com"

__license__ = "MIT"

__version__ = "1.3.4"
__date__ = "2019-08-17"
__release__ = "修复了当 `User.followers` `User.followings` `User.answers` `User.questions` `Question.answers` 为空时产生迭代错误"


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
