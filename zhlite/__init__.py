# -*- coding: utf-8 -*-

from zhlite.zhlite import Auth, User, Question, Answer, Article, Session

__author__ = "zhangbo"
__email__ = "deplives@deplives.com"

__license__ = "MIT"

__version__ = "1.7.1"
__date__ = "2019-09-03"
__release__ = "支持代理"

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


version = Version()


def set_proxy(proxies):
    session = Session()
    session.proxies.update(proxies)
