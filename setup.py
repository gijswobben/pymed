import os
from setuptools import setup
from setuptools import find_packages
from pymed.version import __version__


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="pymed",
    version=__version__,
    author="Gijs Wobben & Michael Bullman",
    author_email=["gijswobben@gmail.com", "mbullman@fredhutch.org"],
    description=("Python library for access to PubMed"),
    license="MIT",
    keywords="PubMed PMC",
    url="https://gitlab.fhcrc.org/cit-bi/pymedfhcrc",
    packages=find_packages(),
    install_requires=["requests>=2.20.0"],
    tests_require=["pytest"],
    long_description_content_type="text/markdown",
    long_description=read("README.md"),
    classifiers=[
        "Topic :: Utilities",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3 :: Only",
    ],
)
