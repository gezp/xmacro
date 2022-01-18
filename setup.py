#!/usr/bin/python3
# -*- coding: utf-8 -*-
from os import path

from setuptools import find_packages, setup

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='xmacro',
    version='1.2.1',
    author='Zhenpeng Ge',
    author_email='zhenpeng.ge@qq.com',
    url='https://github.com/gezp/xmacro',
    description='a simple XML macro tool',
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='MIT',
    keywords=['xml', 'macro', 'xacro', 'xmacro', 'sdformat', 'sdf', 'urdf'],
    include_package_data=True,
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'xmacro = xmacro.xmacro:xmacro_main',
            'xmacro4sdf = xmacro.xmacro4sdf:xmacro4sdf_main',
            'xmacro4urdf = xmacro.xmacro4urdf:xmacro4urdf_main',
        ]
    }
)
