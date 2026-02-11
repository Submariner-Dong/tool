#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name="wjx_survey_tool",
    version="1.0.0",
    description="问卷星自动填写工具",
    author="SubmarinerD",
    packages=find_packages(),
    install_requires=[
        "selenium>=4.15.0",
        "webdriver-manager>=4.0.0", 
        "requests>=2.31.0"
    ],
    python_requires=">=3.7",
    entry_points={
        'console_scripts': [
            'wjx-survey-tool=main:main',
        ],
    },
    include_package_data=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)