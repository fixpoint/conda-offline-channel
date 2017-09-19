import sys
from setuptools import setup, find_packages

NAME = 'conda-offline-channel'


entry_points = {
    'console_scripts': [
        'conda-offline-channel=conda_offline_channel.cli.main_offline_channel:main'
    ],
}

if sys.platform.startswith('win'):
    # Add 'ksservice' in Windows
    entry_points['console_scripts'].append(
        'ksservice=ksocket.service.windows:main'
    )


setup(
    name=NAME,
    version='0.0.0',
    #use_scm_version=True,
    description='',
    #long_description='file:README.rst',
    zip_safe=False,
    packages=[
        'conda_offline_channel',
        'conda_offline_channel.cli',
    ],
    setup_requires=['setuptools_scm'],
    entry_points=entry_points,
)
