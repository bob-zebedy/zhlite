# -*- coding: utf-8 -*-

from zhlite.zhlite import *

__author__ = "zhangbo"
__email__ = "deplives@deplives.com"

__license__ = "MIT"

__version__ = "1.2.0"
__date__ = "2019-08-12"
__release__ = "删除 Answer.save_media() 方法，新增 Answer.save(typed='picture'|'video'|'all') 支持下载视频"


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
