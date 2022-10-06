import os
import sys
import re
from glob import glob
from setuptools import setup, find_packages
import pkg_resources


__pkg_name__ = 'ezcharts'
__author__ = 'cwright'
__description__ = 'eCharts plotting API.'

# Use readme as long description and say its github-flavour markdown
from os import path
this_directory = path.abspath(path.dirname(__file__))
kwargs = {'encoding':'utf-8'} if sys.version_info.major == 3 else {}
with open(path.join(this_directory, 'README.md'), **kwargs) as f:
    __long_description__ = f.read()
__long_description_content_type__ = 'text/markdown'

__path__ = os.path.dirname(__file__)
__pkg_path__ = os.path.join(os.path.join(__path__, __pkg_name__))

# Get the version number from __init__.py
verstrline = open(os.path.join(__pkg_name__, '__init__.py'), 'r').read()
vsre = r"^__version__ = ['\"]([^'\"]*)['\"]"
mo = re.search(vsre, verstrline, re.M)
if mo:
    __version__ = mo.group(1)
else:
    raise RuntimeError('Unable to find version string in "{}/__init__.py".'.format(__pkg_name__))

dir_path = os.path.dirname(__file__)
with open(os.path.join(dir_path, 'requirements.txt')) as fh:
    install_requires = [
        str(requirement) for requirement in
        pkg_resources.parse_requirements(fh)]

data_files = []
extra_requires = {}
extensions = []

setup(
    name=__pkg_name__,
    version=__version__,
    url='https://github.com/epi2me-labs/{}'.format(__pkg_name__),
    author=__author__,
    author_email='{}@nanoporetech.com'.format(__author__),
    description=__description__,
    long_description=__long_description__,
    long_description_content_type=__long_description_content_type__,
    dependency_links=[],
    ext_modules=extensions,
    install_requires=install_requires,
    tests_require=[].extend(install_requires),
    extras_require=extra_requires,
    # don't include any testing subpackages in dist
    packages=find_packages(exclude=['*.test', '*.test.*', 'test.*', 'test']),
    #package_data={__pkg_name__:[os.path.join('data', '*')]},
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'console_scripts': [
            '{0} = {0}:cli'.format(__pkg_name__)
        ]
    },
    scripts=[]
)
