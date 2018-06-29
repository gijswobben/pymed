import os
from setuptools import setup
from version import __version__


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="pymed",
    version=__version__,
    author="Gijs Wobben",
    author_email="gijswobben@gmail.com",
    description=(
        "GraphQL schema (in Python) for PubMed"
    ),
    license="MIT",
    keywords="PubMed GraphQL",
    url="http://packages.python.org/pymed",
    packages=[
        "pymed"
    ],
    install_requires=[
        "graphene==2.1",
        "requests==2.18.4"
    ],
    tests_require=["pytest"],
    long_description_content_type='text/markdown',
    long_description=read("README.md"),
    classifiers=[
        "Topic :: Utilities",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3 :: Only"
    ],
)
