"""Setup module for stabledracor

See: https://github.com/dracor-org/stabledracor
"""
from setuptools import setup

# Get the long description from the README file
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="stabledracor",
    packages=["stabledracor"],
    version="0.1.0",
    license="GPLv3",
    description="Python package to simplify setting up a local DraCor system using Docker.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Ingo Börner",
    author_email="ingo.boerner@uni-potsdam.de",
    url="https://github.com/dracor-org/stabledracor",
    keywords=["drama corpus", "programmable corpus", "dracor", "docker"],
    install_requires=[
        "requests>=2.31.0",
        "PyYAML>=6.0"

    ],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Console",
        "Framework :: Jupyter :: JupyterLab",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: MacOS",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 3.11",
        "Topic :: Utilities"
    ]
)
