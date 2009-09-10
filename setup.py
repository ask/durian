#!/usr/bin/env python
# -*- coding: utf-8 -*-
import codecs
import sys
import os

try:
    from setuptools import setup, find_packages, Command
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages, Command

import durian


class RunTests(Command):
    description = "Run the django test suite from the testproj dir."

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        this_dir = os.getcwd()
        testproj_dir = os.path.join(this_dir, "testproj")
        os.chdir(testproj_dir)
        sys.path.append(testproj_dir)
        from django.core.management import execute_manager
        os.environ["DJANGO_SETTINGS_MODULE"] = os.environ.get(
                        "DJANGO_SETTINGS_MODULE", "settings")
        settings_file = os.environ["DJANGO_SETTINGS_MODULE"]
        settings_mod = __import__(settings_file, {}, {}, [''])
        execute_manager(settings_mod, argv=[
            __file__, "test"])
        os.chdir(this_dir)


install_requires = ["django-unittest-depth",
                    "celery"]

if os.path.exists("README.rst"):
    long_description = codecs.open("README.rst", "r", "utf-8").read()
else:
    long_description = "See http://pypi.python.org/pypi/celery"


setup(
    name='durian',
    version=durian.__version__,
    description=durian.__doc__,
    author=durian.__author__,
    author_email=durian.__contact__,
    url=durian.__homepage__,
    platforms=["any"],
    packages=find_packages(exclude=['ez_setup']),
    zip_safe=False,
    install_requires=install_requires,
    cmdclass = {"test": RunTests},
    classifiers=[
        "Development Status :: 1 - Planning",
        "Framework :: Django",
        "Environment :: Web Environment",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Communications",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: BSD License",
    ],
    long_description=long_description,
)
