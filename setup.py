# -*- coding: UTF-8 -*-
import setuptools

with open("README.md", "r", encoding='utf8') as f:
    long_description = f.read()

setuptools.setup(
    name="zhlite",
    version="1.2.0",
    author="zhangbo",
    author_email="deplives@deplives.com",
    description="zhihu lite client",
    long_description=long_description,
    license="MIT",
    long_description_content_type="text/markdown",
    url="https://github.com/deplives/zhihu",
    packages=['zhlite'],
    install_requires=[
        'requests==2.21.0',
        'beautifulsoup4==4.7.1',
        'lxml==4.3.4',
        'PyExecJS==1.5.1',
        'Pillow==6.0.0'
    ],
    classifiers=(
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
