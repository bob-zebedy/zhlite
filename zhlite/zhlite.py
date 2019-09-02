# -*- coding: utf-8 -*-

import base64
import getpass
import hashlib
import hmac
import json
import os
import re
import sys
import threading
from datetime import datetime
from http import cookiejar
from time import sleep, time
from urllib import parse
from urllib.parse import urlencode

import execjs
import requests
from bs4 import BeautifulSoup


def singleton(cls):
    instance = {}

    def inner():
        if cls not in instance:
            instance[cls] = cls()
        return instance[cls]
    return inner


@singleton
class Session(requests.Session):
    pass


class LoginError(Exception):
    pass


class ZhliteBase(object):

    def __addattribute__(self):
        try:
            for k, v in self.info.items():
                self.__dict__[k] = v
        except Exception:
            pass

    def __ut2date__(self, ut):
        return datetime.fromtimestamp(ut).strftime("%Y-%m-%d %H:%M:%S") if ut else "0000-00-00 00:00:00"

    def __html2text__(self, html):
        pattern = re.compile(r"<.*?>")
        return pattern.sub("", html)

    def __videoinfo__(self, url):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
        }
        param = parse.parse_qs(parse.urlparse(url).query)
        target = param['target'][0]
        videoid = target.split(r'/')[-1]
        try:
            response = requests.get(f"https://lens.zhihu.com/api/v4/videos/{videoid}", headers=headers, timeout=10)
            info = json.loads(response.text, encoding="utf-8")
            if 'HD' in info['playlist']:
                return info['playlist']['HD']['play_url'], info['title'], info['playlist']['HD']['format']
            elif 'SD' in info['playlist']:
                return info['playlist']['SD']['play_url'], info['title'], info['playlist']['SD']['format']
            elif 'LD' in info['playlist']:
                return info['playlist']['LD']['play_url'], info['title'], info['playlist']['LD']['format']
            else:
                return
        except Exception:
            return

    def __download__(self, url):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
        }
        try:
            sleep(0.2)
            response = requests.get(url, headers=headers, stream=True, timeout=10)
            if response.status_code == 200:
                return response.content
            else:
                raise ConnectionError(response.status_code, response.url)
        except Exception as e:
            raise e

    def request(self, api, payloads=None):
        try:
            sleep(0.2)
            response = self.session.get(api, params=payloads, timeout=10)
            if response.status_code == 200:
                return json.loads(response.text, encoding="utf-8")
            elif response.status_code == 410:
                return False
            elif response.status_code == 403:
                raise ConnectionError(response.status_code, response.text)
            else:
                raise ConnectionError(response.status_code, response.url)
        except Exception as e:
            raise e


class Auth(ZhliteBase):
    platform = sys.platform
    info = {
        "platform": platform
    }

    def __init__(self):
        self.session = Session()
        self.session.cookies = cookiejar.LWPCookieJar("cookies.txt")
        self.session.headers = {
            "Host": "www.zhihu.com",
            "Referer": "https://www.zhihu.com/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
        }

        self.login()

    def login(self, relogin=False):
        if not relogin:
            try:
                self.session.cookies.load(ignore_discard=True)
                if self.islogin:
                    return
                else:
                    raise LoginError()
            except Exception:
                pass

        api = "https://www.zhihu.com/api/v3/oauth/sign_in"

        payloads = {
            "client_id": "c3cef7c66a1843f8b3a9e6a1e3160e20",
            "grant_type": "password",
            "source": "com.zhihu.web",
            "lang": "en",
            "ref_source": "homepage",
            "utm_source": "",
            "username": input("手机: +86 "),
            "password": getpass.getpass("密码: "),
        }

        timestamp = self.__gettimestamp__()
        payloads.update({
            "captcha": self.__getcaptcha__(),
            "timestamp": timestamp,
            "signature": self.__getsignature__(timestamp)
        })

        headers = self.session.headers.copy()
        headers.update({
            "content-type": "application/x-www-form-urlencoded",
            "x-zse-83": "3_1.1",
            "x-xsrftoken": self.__getxsrf__()
        })

        data = self.__encrypt__(payloads)

        response = self.session.post(api, data=data, headers=headers)
        if self.islogin:
            self.session.cookies.save()
        else:
            raise LoginError(json.loads(response.text, encoding="utf-8")["error"]["message"])

    def __getcaptcha__(self):
        api = "https://www.zhihu.com/api/v3/oauth/captcha?lang=en"

        response_get = self.session.get(api)
        json_get = json.loads(response_get.text, encoding="utf-8")

        if json_get["show_captcha"]:
            response_put = self.session.put(api)
            json_put = json.loads(response_put.text, encoding="utf-8")
            imgb64 = json_put["img_base64"].replace(r"\n", "")
            with open("captcha.jpg", "wb") as f:
                f.write(base64.b64decode(imgb64))

            capt = input("验证码: ")
            resp = self.session.post(api, data={"input_text": capt})
            if resp.status_code == 201:
                return capt
            else:
                self.__getcaptcha__()

    def __gettimestamp__(self):
        return int(time()*1000)

    def __getsignature__(self, timestamp):
        ha = hmac.new(
            b"d1b964811afb40118a12068ff74a12f4",
            digestmod=hashlib.sha1
        )

        grant_type = "password"
        client_id = "c3cef7c66a1843f8b3a9e6a1e3160e20"
        source = "com.zhihu.web"
        timestamp = str(timestamp)

        ha.update(bytes((grant_type + client_id + source + timestamp), "utf-8"))
        return ha.hexdigest()

    def __getxsrf__(self):
        url = "https://www.zhihu.com/"
        self.session.get(url, allow_redirects=False)
        for cookie in self.session.cookies:
            if cookie.name == "_xsrf":
                return cookie.value
        raise LoginError("获取 xsrf 失败")

    def __encrypt__(self, payloads):
        jscode = '''function s(t){return(s="function"==typeof Symbol&&"symbol"==typeof Symbol.t?function(t){return typeof t}:function(t){return t&&"function"==typeof Symbol&&t.constructor===Symbol&&t!==Symbol.prototype?"symbol":typeof t})(t)}function i(){}function h(t){this.s=(2048&t)>>11,this.i=(1536&t)>>9,this.h=511&t,this.A=511&t}function A(t){this.i=(3072&t)>>10,this.A=1023&t}function n(t){this.n=(3072&t)>>10,this.e=(768&t)>>8,this.a=(192&t)>>6,this.s=63&t}function e(t){this.i=t>>10&3,this.h=1023&t}function a(){}function c(t){this.n=(3072&t)>>10,this.e=(768&t)>>8,this.a=(192&t)>>6,this.s=63&t}function o(t){this.A=(4095&t)>>2,this.s=3&t}function r(t){this.i=t>>10&3,this.h=t>>2&255,this.s=3&t}function k(t){this.s=(4095&t)>>10,this.i=(1023&t)>>8,this.h=1023&t,this.A=63&t}function B(t){this.s=(4095&t)>>10,this.n=(1023&t)>>8,this.e=(255&t)>>6}function f(t){this.i=(3072&t)>>10,this.A=1023&t}function u(t){this.A=4095&t}function C(t){this.i=(3072&t)>>10}function b(t){this.A=4095&t}function g(t){this.s=(3840&t)>>8,this.i=(192&t)>>6,this.h=63&t}function G(){this.c=[0,0,0,0],this.o=0,this.r=[],this.k=[],this.B=[],this.f=[],this.u=[],this.C=!1,this.b=[],this.g=[],this.G=!1,this.Q=null,this.R=null,this.w=[],this.x=0,this.D={0:i,1:h,2:A,3:n,4:e,5:a,6:c,7:o,8:r,9:k,10:B,11:f,12:u,13:C,14:b,15:g}}Object.defineProperty(exports,"__esModule",{value:!0});var t="1.1",__g={};i.prototype.M=function(t){t.G=!1},h.prototype.M=function(t){switch(this.s){case 0:t.c[this.i]=this.h;break;case 1:t.c[this.i]=t.k[this.A]}},A.prototype.M=function(t){t.k[this.A]=t.c[this.i]},n.prototype.M=function(t){switch(this.s){case 0:t.c[this.n]=t.c[this.e]+t.c[this.a];break;case 1:t.c[this.n]=t.c[this.e]-t.c[this.a];break;case 2:t.c[this.n]=t.c[this.e]*t.c[this.a];break;case 3:t.c[this.n]=t.c[this.e]/t.c[this.a];break;case 4:t.c[this.n]=t.c[this.e]%t.c[this.a];break;case 5:t.c[this.n]=t.c[this.e]==t.c[this.a];break;case 6:t.c[this.n]=t.c[this.e]>=t.c[this.a];break;case 7:t.c[this.n]=t.c[this.e]||t.c[this.a];break;case 8:t.c[this.n]=t.c[this.e]&&t.c[this.a];break;case 9:t.c[this.n]=t.c[this.e]!==t.c[this.a];break;case 10:t.c[this.n]=s(t.c[this.e]);break;case 11:t.c[this.n]=t.c[this.e]in t.c[this.a];break;case 12:t.c[this.n]=t.c[this.e]>t.c[this.a];break;case 13:t.c[this.n]=-t.c[this.e];break;case 14:t.c[this.n]=t.c[this.e]<t.c[this.a];break;case 15:t.c[this.n]=t.c[this.e]&t.c[this.a];break;case 16:t.c[this.n]=t.c[this.e]^t.c[this.a];break;case 17:t.c[this.n]=t.c[this.e]<<t.c[this.a];break;case 18:t.c[this.n]=t.c[this.e]>>>t.c[this.a];break;case 19:t.c[this.n]=t.c[this.e]|t.c[this.a]}},e.prototype.M=function(t){t.r.push(t.o),t.B.push(t.k),t.o=t.c[this.i],t.k=[];for(var s=0;s<this.h;s++)t.k.unshift(t.f.pop());t.u.push(t.f),t.f=[]},a.prototype.M=function(t){t.o=t.r.pop(),t.k=t.B.pop(),t.f=t.u.pop()},c.prototype.M=function(t){switch(this.s){case 0:t.C=t.c[this.n]>=t.c[this.e];break;case 1:t.C=t.c[this.n]<=t.c[this.e];break;case 2:t.C=t.c[this.n]>t.c[this.e];break;case 3:t.C=t.c[this.n]<t.c[this.e];break;case 4:t.C=t.c[this.n]==t.c[this.e];break;case 5:t.C=t.c[this.n]!=t.c[this.e];break;case 6:t.C=t.c[this.n];break;case 7:t.C=!t.c[this.n]}},o.prototype.M=function(t){switch(this.s){case 0:t.o=this.A;break;case 1:t.C&&(t.o=this.A);break;case 2:t.C||(t.o=this.A);break;case 3:t.o=this.A,t.Q=null}t.C=!1},r.prototype.M=function(t){switch(this.s){case 0:for(var s=[],i=0;i<this.h;i++)s.unshift(t.f.pop());t.c[3]=t.c[this.i](s[0],s[1]);break;case 1:for(var h=t.f.pop(),c=[],o=0;o<this.h;o++)c.unshift(t.f.pop());t.c[3]=t.c[this.i][h](c[0],c[1]);break;case 2:for(var n=[],e=0;e<this.h;e++)n.unshift(t.f.pop());t.c[3]=new t.c[this.i](n[0],n[1])}},k.prototype.M=function(t){switch(this.s){case 0:t.f.push(t.c[this.i]);break;case 1:t.f.push(this.h);break;case 2:t.f.push(t.k[this.A]);break;case 3:t.f.push(t.g[this.A])}},B.prototype.M=function(t){switch(this.s){case 0:var s=t.f.pop();t.c[this.n]=t.c[this.e][s];break;case 1:var i=t.f.pop(),h=t.f.pop();t.c[this.e][i]=h;break;case 2:var A=t.f.pop();"window"===A?A={encodeURIComponent:function(t){return encodeURIComponent(t)}}:"navigator"===A&&(A={userAgent:"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"}),t.c[this.n]=eval(A)}},f.prototype.M=function(t){t.c[this.i]=t.g[this.A]},u.prototype.M=function(t){t.Q=this.A},C.prototype.M=function(t){throw t.c[this.i]},b.prototype.M=function(t){var s=this,i=[0];t.k.forEach(function(t){i.push(t)});var h=function(h){var c=new G;return c.k=i,c.k[0]=h,c.J(t.b,s.A,t.g,t.w),c.c[3]};h.toString=function(){return"() { [native code] }"},t.c[3]=h},g.prototype.M=function(t){switch(this.s){case 0:for(var s={},i=0;i<this.h;i++){var h=t.f.pop();s[t.f.pop()]=h}t.c[this.i]=s;break;case 1:for(var c=[],o=0;o<this.h;o++)c.unshift(t.f.pop());t.c[this.i]=c}},G.prototype.v=function(t){for(var s=Buffer.from(t,"base64").toString("binary"),i=[],h=0;h<s.length-1;h+=2)i.push(s.charCodeAt(h)<<8|s.charCodeAt(h+1));this.b=i},G.prototype.y=function(t){for(var s=Buffer.from(t,"base64").toString("binary"),i=66,h=[],c=0;c<s.length;c++){var o=24^s.charCodeAt(c)^i;h.push(String.fromCharCode(o)),i=o}return h.join("")},G.prototype.F=function(t){var s=this;this.g=t.map(function(t){return"string"==typeof t?s.y(t):t})},G.prototype.J=function(t,s,i){for(s=s||0,i=i||[],this.o=s,"string"==typeof t?(this.F(i),this.v(t)):(this.b=t,this.g=i),this.G=!0,this.x=Date.now();this.G;){var h=this.b[this.o++];if("number"!=typeof h)break;var c=Date.now();if(500<c-this.x)return;this.x=c;try{this.M(h)}catch(t){if(this.R=t,!this.Q)throw"execption at "+this.o+": "+t;this.o=this.Q}}},G.prototype.M=function(t){var s=(61440&t)>>12;new this.D[s](t).M(this)},(new G).J("4AeTAJwAqACcAaQAAAAYAJAAnAKoAJwDgAWTACwAnAKoACACGAESOTRHkQAkAbAEIAMYAJwFoAASAzREJAQYBBIBNEVkBnCiGAC0BjRAJAAYBBICNEVkBnDGGAC0BzRAJACwCJAAnAmoAJwKoACcC4ABnAyMBRAAMwZgBnESsA0aADRAkQAkABgCnA6gABoCnA+hQDRHGAKcEKAAMQdgBnFasBEaADRAkQAkABgCnBKgABoCnBOhQDRHZAZxkrAUGgA0QJEAJAAYApwVoABgBnG6sBYaADRAkQAkABgCnBegAGAGceKwGBoANECRACQAnAmoAJwZoABgBnIOsBoaADRAkQAkABgCnBugABoCnByhQDRHZAZyRrAdGgA0QJEAJAAQACAFsB4gBhgAnAWgABIBNEEkBxgHEgA0RmQGdJoQCBoFFAE5gCgFFAQ5hDSCJAgYB5AAGACcH4AFGAEaCDRSEP8xDzMQIAkQCBoFFAE5gCgFFAQ5hDSCkQAkCBgBGgg0UhD/MQ+QACAIGAkaBxQBOYGSABoAnB+EBRoIN1AUCDmRNJMkCRAIGgUUATmAKAUUBDmENIKRACQIGAEaCDRSEP8xD5AAIAgYCRoHFAI5gZIAGgCcH4QFGgg3UBQQOZE0kyQJGAMaCRQ/OY+SABoGnCCEBTTAJAMYAxoJFAY5khI/Nk+RABoGnCCEBTTAJAMYAxoJFAw5khI/Nk+RABoGnCCEBTTAJAMYAxoJFBI5khI/Nk+RABoGnCCEBTTAJAMYBxIDNEEkB3JsHgNQAA==",0,["BRgg","BSITFQkTERw=","LQYfEhMA","PxMVFBMZKB8DEjQaBQcZExMC","","NhETEQsE","Whg=","Wg==","MhUcHRARDhg=","NBcPBxYeDQMF","Lx4ODys+GhMC","LgM7OwAKDyk6Cg4=","Mx8SGQUvMQ==","SA==","ORoVGCQgERcCAxo=","BTcAERcCAxo=","BRg3ABEXAgMaFAo=","SQ==","OA8LGBsP","GC8LGBsP","Tg==","PxAcBQ==","Tw==","KRsJDgE=","TA==","LQofHg4DBwsP","TQ==","PhMaNCwZAxoUDQUeGQ==","PhMaNCwZAxoUDQUeGTU0GQIeBRsYEQ8=","Qg==","BWpUGxkfGRsZFxkbGR8ZGxkHGRsZHxkbGRcZG1MbGR8ZGxkXGRFpGxkfGRsZFxkbGR8ZGxkHGRsZHxkbGRcZGw==","ORMRCyk0Exk8LQ==","ORMRCyst"]);var Q=function(t){return __g._encrypt(t)};'''
        js = execjs.compile(jscode)
        return js.call("Q", urlencode(payloads))

    @property
    def islogin(self):
        url = "https://www.zhihu.com/signup"
        response = self.session.get(url, allow_redirects=False)
        if response.status_code == 302:
            return True
        return False

    @property
    def profile(self):
        api = "https://www.zhihu.com/api/v4/me"
        payloads = {
            "include": "follower_count,following_count,answer_count,question_count,articles_count,voteup_count,visits_count"
        }
        info = self.request(api, payloads)
        return User(info["id"])


class User(ZhliteBase):
    def __init__(self, ids):
        self.session = Session()
        self.ids = ids

        self.anonymous = ["", "0", 0, None]

        self.gendermap = {
            1: "男",
            0: "女",
            -1: "未知",
        }

        self.info = {
            "id": "",                                   # 自定义ID
            "uid": "",                                  # 内部ID
            "name": "",                                 # 显示名字
            "gender": self.gendermap[-1],               # 性别 0:女 1:男 -1:未知
            "employments": "",                          # 职业
            "educations": "",                           # 教育
            "locations": "",                            # 地区
            "avatar": "",                               # 用户头像
            "headline": "",                             # 个人简介
            "is_vip": "",                               # 盐选会员
            "is_org": "",                               # 机构号|个人号
            "follower_count": "",                       # 关注者数量
            "following_count": "",                      # 关注的人数量
            "answer_count": "",                         # 回答数量
            "question_count": "",                       # 提问数量
            "article_count": "",                        # 文章数量
            "voteup_count": "",                         # 获得赞同数量
            "visit_count": ""                           # 来访者数量
        }

        self.__getinfo__()
        self.__addattribute__()

    def __eq__(self, anouser):
        if isinstance(anouser, self.__class__):
            if self and anouser:
                return self.info["uid"] == anouser.info["uid"]
            else:
                return False
        else:
            raise TypeError("A non-User Object")

    def __hash__(self):
        return hash(self.info["uid"])

    def __bool__(self):
        return True if self.info["uid"] not in self.anonymous else False

    def __getinfo__(self):
        api = f"https://www.zhihu.com/api/v4/members/{self.ids}"

        payloads = {
            "include": "follower_count,following_count,answer_count,question_count,articles_count,voteup_count,visits_count,employments,educations,locations,is_org"
        }

        if self.ids in self.anonymous:
            self.info["name"] = "[匿名用户]"
        else:
            info = self.request(api, payloads)
            if info:
                self.info.update({
                    "id": info["url_token"],
                    "uid": info["id"],
                    "name": info["name"],
                    "avatar": info["avatar_url"],
                    "gender": self.gendermap[info["gender"]],
                    "employments": {i.get("company", {}).get("name", ""): i.get("job", {}).get("name", "") for i in info["employments"]},
                    "educations": {i.get("school", {}).get("name", ""): i.get("major", {}).get("name", "") for i in info["educations"]},
                    "locations": [i["name"] for i in info["locations"]],
                    "headline": info["headline"],
                    "is_vip": info["vip_info"]["is_vip"],
                    "is_org": info["is_org"],
                    "follower_count": info["follower_count"],
                    "following_count": info["following_count"],
                    "answer_count": info["answer_count"],
                    "question_count": info["question_count"],
                    "article_count": info["articles_count"],
                    "voteup_count": info["voteup_count"],
                    "visit_count": info["visits_count"]
                })
            else:
                self.info.update({
                    "name": "[已注销]"
                })

    @property
    def followers(self):
        api = f"https://www.zhihu.com/api/v4/members/{self.info['id']}/followers"
        offset = 0
        payloads = {
            "limit": 20,
            "offset": offset,
        }
        info = self.request(api, payloads)
        is_end = info["paging"]["is_end"]

        if info["data"]:
            for user in info["data"]:
                yield User(user["url_token"])

        while not is_end:
            offset += 20
            payloads = {
                "limit": 20,
                "offset": offset,
            }
            try:
                info = self.request(api, payloads)
                is_end = info["paging"]["is_end"]

                for user in info["data"]:
                    yield User(user["url_token"])
            except Exception:
                pass

    @property
    def followings(self):
        api = f"https://www.zhihu.com/api/v4/members/{self.info['id']}/followees"
        offset = 0
        payloads = {
            "limit": 20,
            "offset": offset,
        }
        info = self.request(api, payloads)
        is_end = info["paging"]["is_end"]

        if info["data"]:
            for user in info["data"]:
                yield User(user["url_token"])

        while not is_end:
            offset += 20
            payloads = {
                "limit": 20,
                "offset": offset,
            }
            try:
                info = self.request(api, payloads)
                is_end = info["paging"]["is_end"]

                for user in info["data"]:
                    yield User(user["url_token"])
            except Exception:
                pass

    @property
    def answers(self):
        api = f"https://www.zhihu.com/api/v4/members/{self.info['id']}/answers"
        offset = 0
        payloads = {
            "limit": 20,
            "offset": offset,
        }
        info = self.request(api, payloads)
        is_end = info["paging"]["is_end"]

        if info["data"]:
            for answer in info["data"]:
                yield Answer(answer["id"])

        while not is_end:
            offset += 20
            payloads = {
                "limit": 20,
                "offset": offset,
            }
            info = self.request(api, payloads)
            is_end = info["paging"]["is_end"]

            for answer in info["data"]:
                yield Answer(answer["id"])

    @property
    def questions(self):
        api = f"https://www.zhihu.com/api/v4/members/{self.info['id']}/questions"
        offset = 0
        payloads = {
            "limit": 20,
            "offset": offset,
        }
        info = self.request(api, payloads)
        is_end = info["paging"]["is_end"]

        if info["data"]:
            for question in info["data"]:
                yield Question(question["id"])

        while not is_end:
            offset += 20
            payloads = {
                "limit": 20,
                "offset": offset,
            }
            try:
                info = self.request(api, payloads)
                is_end = info["paging"]["is_end"]

                for question in info["data"]:
                    yield Question(question["id"])
            except Exception:
                pass

    @property
    def articles(self):
        api = f"https://www.zhihu.com/api/v4/members/{self.info['id']}/articles"
        offset = 0
        payloads = {
            "limit": 20,
            "offset": offset,
        }
        info = self.request(api, payloads)
        is_end = info["paging"]["is_end"]

        if info["data"]:
            for article in info["data"]:
                yield Article(article["id"])

        while not is_end:
            offset += 20
            payloads = {
                "limit": 20,
                "offset": offset,
            }
            try:
                info = self.request(api, payloads)
                is_end = info["paging"]["is_end"]

                for article in info["data"]:
                    yield Article(article["id"])
            except Exception:
                pass


class Answer(ZhliteBase):

    def __init__(self, id, **kwargs):
        self.session = Session()
        self.info = {
            "id": id,
            "type": kwargs.get("type", ""),
            "author": User(kwargs.get("author", None)),
            "excerpt": kwargs.get("excerpt", ""),
            "content": kwargs.get("content", ""),
            "text": self.__html2text__(kwargs.get("content", "")),
            "comment_count": kwargs.get("comment_count", ""),
            "voteup_count": kwargs.get("voteup_count", ""),
            "created": self.__ut2date__(kwargs.get("created", None)),
            "updated": self.__ut2date__(kwargs.get("updated", None)),
            "question": kwargs.get("question", "")
        }

        if not kwargs:
            self.__getinfo__()

        self.__addattribute__()

    def __eq__(self, anoanswer):
        if isinstance(anoanswer, self.__class__):
            if self and anoanswer:
                return self.info["id"] == anoanswer.info["id"]
            else:
                return False
        else:
            raise TypeError("A non-Anoanswer Object")

    def __hash__(self):
        return hash(self.info["id"])

    def __getinfo__(self):
        api = f"https://www.zhihu.com/api/v4/answers/{self.info['id']}"
        payloads = {
            "include": "content,excerpt,comment_count,voteup_count"
        }
        info = self.request(api, payloads)

        self.info["type"] = info["answer_type"]
        self.info["author"] = User(info["author"]["id"])
        self.info["excerpt"] = info["excerpt"]
        self.info["content"] = info["content"]
        self.info["text"] = self.__html2text__(info["content"])
        self.info["comment_count"] = info["comment_count"]
        self.info["voteup_count"] = info["voteup_count"]
        self.info["created"] = self.__ut2date__(info["created_time"])
        self.info["updated"] = self.__ut2date__(info["updated_time"])
        self.info["question"] = Question(info["question"]["id"])

    @property
    def images(self):
        default_path = os.path.join(
            str(self.info["question"].title[:-1] + "-" + str(self.info["question"].id)),
            str(self.info["id"])
        )
        soupic = BeautifulSoup(self.info["content"], "lxml")
        noscript = soupic.find_all("noscript")

        for imgtag in noscript:
            if imgtag.img.has_attr("data-original"):
                url = imgtag.img["data-original"]
            else:
                url = imgtag.img["src"]
            yield Image(url, default_path)

    @property
    def videos(self):
        default_path = os.path.join(
            str(self.info["question"].title[:-1] + "-" + str(self.info["question"].id)),
            str(self.info["id"])
        )
        soupvd = BeautifulSoup(self.info["content"], "lxml")
        vdlink = soupvd.find_all("a", {"class": "video-box"})
        for vd in vdlink:
            if vd.has_attr("href"):
                urlinfo = self.__videoinfo__(vd["href"])
                yield Video(urlinfo, default_path)


class Question(ZhliteBase):

    def __init__(self, id):
        self.session = Session()
        self.info = {
            "id": id,
            "title": None,
            "detail": None,
            "topics": None,
            "type": None,
            "created": None,
            "updated": None,
            "author": None,
        }

        self.__getinfo__()

        self.__addattribute__()

    def __eq__(self, anoquestion):
        if isinstance(anoquestion, self.__class__):
            if self and anoquestion:
                return self.info["id"] == anoquestion.info["id"]
            else:
                return False
        else:
            raise TypeError("A non-Question Object")

    def __hash__(self):
        return hash(self.info["id"])

    def __getinfo__(self):
        api = f"https://www.zhihu.com/api/v4/questions/{self.info['id']}"
        payloads = {
            "include": "question.detail,author,topics"
        }
        info = self.request(api, payloads)

        self.info["title"] = info["title"]
        self.info["detail"] = self.__html2text__(info["detail"])
        self.info["topics"] = [i["name"] for i in info["topics"]]
        self.info["type"] = info["question_type"]
        self.info["created"] = self.__ut2date__(info["created"])
        self.info["updated"] = self.__ut2date__(info["updated_time"])
        self.info["author"] = User(info["author"]["id"])

    @property
    def answers(self):
        api = f"https://www.zhihu.com/api/v4/questions/{self.info['id']}/answers"
        payloads = {
            "include": "content,excerpt,comment_count,voteup_count",
            "offset": 0,
            "limit": 10,
            "sort_by": "created"
        }
        info = self.request(api, payloads)

        is_end = info["paging"]["is_end"]
        nexturl = info["paging"]["next"]

        if info["data"]:
            for answer in info["data"]:
                yield Answer(
                    id=answer["id"],
                    type=answer["answer_type"],
                    author=answer["author"]["id"],
                    excerpt=answer["excerpt"],
                    content=answer["content"],
                    text=answer["content"],
                    comment_count=answer["comment_count"],
                    voteup_count=answer["voteup_count"],
                    created=answer["created_time"],
                    updated=answer["updated_time"],
                    question=Question(answer["question"]["id"])
                )
        while not is_end:
            try:
                info = self.request(nexturl)
                is_end = info["paging"]["is_end"]
                nexturl = info["paging"]["next"]

                for answer in info["data"]:
                    yield Answer(
                        id=answer["id"],
                        type=answer["answer_type"],
                        author=answer["author"]["id"],
                        excerpt=answer["excerpt"],
                        content=answer["content"],
                        text=answer["content"],
                        comment_count=answer["comment_count"],
                        voteup_count=answer["voteup_count"],
                        created=answer["created_time"],
                        updated=answer["updated_time"],
                        question=Question(answer["question"]["id"])
                    )
            except Exception:
                pass


class Article(ZhliteBase):
    def __init__(self, id):
        self.session = Session()
        self.info = {
            "id": id,
            "title": "",
            "author": None,
            "created": None,
            "updated": None,
            "topics": None,
            "excerpt": "",
            "content": "",
            "text": "",
            "comment_count": None,
            "voteup_count": None,
        }

        self.__getinfo__()
        self.__addattribute__()

    def __eq__(self, anoarticle):
        if isinstance(anoarticle, self.__class__):
            if self and anoarticle:
                return self.info["id"] == anoarticle.info["id"]
            else:
                return False
        else:
            raise TypeError("A non-Article Object")

    def __hash__(self):
        return hash(self.info["id"])

    def __getinfo__(self):
        api = f"https://www.zhihu.com/api/v4/articles/{self.info['id']}"
        info = self.request(api)

        self.info.update({
            "title": info["title"],
            "author": User(info["author"].get("id", "")),
            "created": self.__ut2date__(info["created"]),
            "updated": self.__ut2date__(info["updated"]),
            "topics": [i["name"] for i in info["topics"]],
            "excerpt": info["excerpt"],
            "content": info["content"],
            "text": self.__html2text__(info["content"]),
            "comment_count": info["comment_count"],
            "voteup_count": info["voteup_count"]
        })


class Image(ZhliteBase):
    def __init__(self, url, default_path):
        self.url = url
        self.default_path = default_path

    def save(self, path=None):
        _path_ = path if path else self.default_path
        try:
            os.makedirs(_path_)
        except Exception:
            pass
        data = self.__download__(self.url)

        with open(os.path.join(_path_, os.path.basename(self.url)), "wb") as f:
            print(f.name)
            f.write(data)


class Video(ZhliteBase):
    def __init__(self, urlinfo, default_path):
        self.urlinfo = urlinfo
        self.default_path = default_path

    def save(self, path=None):
        _path_ = path if path else self.default_path
        try:
            os.makedirs(_path_)
        except Exception:
            pass

        if self.urlinfo[1] is None or self.urlinfo[1] == "":
            filename = "".join((str(time()*1000), ".", self.urlinfo[-1]))
        else:
            filename = "".join((self.urlinfo[1], ".", self.urlinfo[-1]))

        data = self.__download__(self.urlinfo[0])

        with open(os.path.join(_path_, filename), "wb") as f:
            print(f.name)
            f.write(data)
