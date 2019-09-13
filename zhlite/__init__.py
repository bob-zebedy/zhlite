# -*- coding: utf-8 -*-

import execjs
from zhlite.zhlite import Answer, Article, Auth, Question, Session, User

__author__ = "zhangbo"
__email__ = "deplives@deplives.com"

__license__ = "MIT"

__version__ = "1.8.3"
__date__ = "2019-09-13"
__release__ = "新增导入时检查 js 环境"

__all__ = ["Auth", "User", "Question", "Answer", "Article"]


class Version(object):

    def __init__(self):
        self.info = {
            "version": __version__,
            "date": __date__,
            "release": __release__
        }

    def __str__(self):
        return " ".join([f"{k}: {v}" for k, v in self.info.items()])


def check_jsenv():
    """
    Description: Check the js runtime environment

    @return: `True` or `False`
    """
    try:
        execjs.get()
    except Exception:
        raise EnvironmentError("未发现js运行环境")


version = Version()
check_jsenv()


def set_proxy(proxies):
    session = Session()
    session.proxies.update(proxies)
