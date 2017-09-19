import sys
from io import open
from setuptools import setup, find_packages

NAME = 'conda-offline-channel'


def read(filename):
    import os

    BASE_DIR = os.path.dirname(__file__)
    filename = os.path.join(BASE_DIR, filename)
    with open(filename, 'r', encoding='utf-8') as fi:
        return fi.read()


def readlist(filename):
    rows = read(filename).split("\n")
    rows = [x.strip() for x in rows if x.strip()]
    return rows


setup(
    name=NAME,
    use_scm_version=True,
    description='Build an offline conda channel which contains all requirements',
    long_description=read('README.rst'),
    author='lambdalisue',
    author_email='lambdalisue@hashnote.net',
    url='https://github.com/lambdalisue/conda-offline-channel',
    zip_safe=False,
    packages=[
        'conda_offline_channel',
        'conda_offline_channel.cli',
    ],
    setup_requires=['setuptools_scm'],
    install_requires=readlist('requirements.txt'),
    entry_points={
        'console_scripts': [
            'conda-offline-channel=conda_offline_channel.cli.main_offline_channel:main'
        ],
    }
)
