# zhlite
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/zhlite?style=flat-square)
![GitHub top language](https://img.shields.io/github/languages/top/deplives/zhlite?style=flat-square)

![GitHub release](https://img.shields.io/github/release/deplives/zhlite?style=flat-square)
![GitHub Release Date](https://img.shields.io/github/release-date/deplives/zhlite?style=flat-square)
![PyPI - Wheel](https://img.shields.io/pypi/wheel/zhlite?style=flat-square)

![GitHub](https://img.shields.io/github/license/deplives/zhlite?style=flat-square)

# 说明
zhlite 是一个知乎的 Python 轻量客户端，全部功能全部采用知乎官方非公布 api 实现。因为很多接口需要登陆才能访问，所以 `zhlite` 需要登录才可以稳定使用。

目前对于所有 `zhlite` 获取的信息，均只可以查看不可以修改。
# 功能
 - [x] 用户登录
 - [x] 登陆用户的基本信息
 - [x] 登陆用户的关注和被关注信息
 - [x] 登陆用户的提问
 - [x] 登陆用户的回答
 - [x] 以登陆用户的身份访问问题
 - [x] 以登录用户的身份访问回答
 - [x] 批量下载回答中的图片
 - [x] 批量下载回答中的视频
 - [ ] 获取回答的评论
# 安装
`pip3 install zhlite`
# 使用
`zhlite` 有几个关键核心类：
 1. Auth(用户认证模块)
 2. User(用户模块)
 3. Question(问题模块)
 4. Answer(回答模块)
 
## 模块说明

### Auth
| 属性 | 类型 | 描述 |
| :----:| :----: | :----: |
| login() | method | 用户登陆 |
| islogin | bool | 是否登陆状态 |
| profile | User Object | 登陆用户 |
| platform | str | 当前运行的系统类型 |

### User
| 属性 | 类型 | 描述 |
| :----:| :----: | :----: |
| id | str | 用户自定义ID |
| uid | str | 用户ID |
| name | str | 显示名字 |
| gender | str | 性别 0:女 1:男 -1:未知 |
| avatar | str | 用户头像 |
| headline | str | 个人简介 |
| is_vip | bool | 盐选会员 |
| follower_count | int | 关注者数量 |
| followers | generator | 关注者 |
| following_count | int | 关注的人数量 |
| followings | generator | 关注的人 |
| answer_count | int | 回答数量 |
| answers | generator | 回答 |
| question_count | int | 提问数量 |
| questions | generator | 提问 |
| article_count | int | 文章数量 |
| voteup_count | int | 获得赞同数量 |
| visit_count | int | 来访者数量 |

### Question
| 属性 | 类型 | 描述 |
| :----:| :----: | :----: |
| id | int | 问题ID |
| title | str | 问题标题 |
| detail | str | 问题描述 |
| topics | list | 问题标签 |
| type | str | 问题状态 |
| created | datetime | 提问时间 |
| updated | datetime | 最后一次修改时间 |
| author | User Object | 提问人 |
| answers | generator | 回答 |

### Answer
| 属性 | 类型 | 描述 |
| :----:| :----: | :----: |
| id | int | 回答ID |
| type | str | 回答状态 |
| author | User Object | 回答者 |
| excerpt | str | 摘要 |
| content | str | 回答(包含HTML信息) |
| text | str | 回答(不包含HTML信息) |
| comment_count | int | 评论数 |
| voteup_count | int | 赞同数 |
| created | datetime | 回答时间 |
| updated | datetime | 最后一次修改时间 |
| question | Question Object | 对应的问题 |
| save() | method | 保存回答中的图片和视频 |

# 使用

## 用户认证(Auth)
第一次实例化 `Auth` 对象时需要通过手机号和密码登陆，之后会生成一个 `cookies.txt` 文件保存登录信息，以后无需再次重复登陆。如需重新登陆，可以通过 `.login(relogin=True)` 强制重新登陆，并刷新 `cookies.txt` 文件  
**注意：短时间内多次通过密码登陆会导致账户异常，账户异常会强制要求用户更改密码并短时间内锁定ip**
```python
>>> from zhlite import Auth
>>> auth = Auth()
>>> auth.login(relogin=True)
```
## 登陆用户
用户登陆之后可通过 `.mine` 获得一个 `User` 对象为已登录用户
```python
>>> from zhlite import Auth
>>> auth = Auth()
>>> auth.mine
<zhlite.zhlite.User object at 0x0000024C6C989630>
```
## 用户(User)
```python
>>> from zhlite import Auth, User, Question, Answer
>>> auth = Auth()
>>> user = User('zhihuadmin')       # 知乎小管家
>>> user
<zhlite.zhlite.User object at 0x00000293F66A81D0>
>>> user.id
'zhihuadmin'
>>> user.name
'知乎小管家'
>>> user.questions
<generator object User.questions at 0x00000293F67620C0>
>>> list(user.questions)        # 谨慎用 list() 如果用户的提问数量很多会导致性能问题
[<zhlite.zhlite.Question object at 0x00000293F77164E0>, <zhlite.zhlite.Question object at 0x00000293F77FD1D0>, <zhlite.zhlite.Question object at 0x00000293F76AB048>, <zhlite.zhlite.Question object at 0x00000293F6691C18>, <zhlite.zhlite.Question object at 0x00000293F7582E80>, <zhlite.zhlite.Question object at 0x00000293F66A80B8>, <zhlite.zhlite.Question object at 0x00000293F758E390>, <zhlite.zhlite.Question object at 0x00000293F7716400>, <zhlite.zhlite.Question object at 0x00000293F6691BE0>, <zhlite.zhlite.Question object at 0x00000293F76ECA90>]
```
## 问题(Question)
```python
>>> from zhlite import Auth
>>> auth = Auth()
>>> question = Question('19550225')
>>> question
<zhlite.zhlite.Question object at 0x00000293F76ECF28>
>>> question.title
'如何使用知乎？'
>>> question.author
<zhlite.zhlite.User object at 0x00000293F76EC8D0>
>>> question.created
'2010-12-20 03:27:20'
>>> question.answers
<generator object Question.answers at 0x00000293F67622A0>
```
## 回答(Answer)
```python
>>> answer = Answer('95070154')
>>> answer
<zhlite.zhlite.Answer object at 0x00000293F77FD1D0>
>>> answer.excerpt
'本问题隶属于「知乎官方指南」：属于「知乎官方指南」的问答有哪些？ -- 在知乎上回答问题有一个基本原则：尽可能提供详细的解 释和说明。 不要灌水——不要把「评论」当作「答案」来发布。 如果你对问题本身或别人的答案有自己的看法，你可以通过「评论」来进行，不要把评论当作答案来发布。那样的话，该回答会被其他用户点击「没有帮助」而折叠起来，反而起不到实际效果，也无助于提供高质量的答案。 --------关于回答--------- …'
>>> answer.comment_count
11
>>> answer.created
'2016-04-13 13:48:52'
>>> answer.question
<zhlite.zhlite.Question object at 0x00000293F76AB048>
```
