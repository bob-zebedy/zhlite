# -*- coding: UTF-8 -*-
import setuptools
from zhlite import __version__, __author__, __email__

with open("README.md", "r", encoding='utf8') as f:
    long_description = f.read()

setuptools.setup(
    name="zhlite",
    version=__version__,
    author=__author__,
    author_email=__email__,
    description="zhlite",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    url="https://github.com/deplives/zhlite",
    packages=['zhlite'],
    install_requires=[
        'requests==2.21.0',
        'beautifulsoup4==4.7.1',
        'lxml==4.6.3',
        'PyExecJS==1.5.1',
        'Pillow==8.3.2'
    ],
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
    ]

)
