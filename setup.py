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
        "graphene"
    ],
    tests_require=["pytest"],
    long_description=read("README.md"),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities"
    ],
)
