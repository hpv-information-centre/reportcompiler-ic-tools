""" Module for installing module as pip package """
import os
from setuptools import find_packages, setup
import sys

sys.path.insert(0, os.path.abspath(__file__))
from reportcompiler_ic_tools import __version__

module_name = 'reportcompiler-ic-tools'
module_dir_name = 'reportcompiler_ic_tools'

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

os.chdir(
    os.path.normpath(
        os.path.join(os.path.abspath(__file__), os.pardir)))


def package_files(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join(path, filename))
    return paths

data_files = []
data_dirs = ['data', 'templates']
for data_dir in data_dirs:
    data_files.extend(
        package_files(
            os.path.normpath(
                os.path.join(
                    os.path.abspath(__file__),
                    os.pardir,
                    module_dir_name,
                    data_dir))))

setup(
    name=module_name,
    version=__version__,
    packages=find_packages('.', exclude=['test']),
    include_package_data=True,
    package_data={module_dir_name: data_files},
    license='MIT License',
    description='The HPV Information Center Report Compiler '
                'tools provide methods to easily take advantage of the data '
                'fetched by the Report Compiler IC Fetcher in a context '
                'generation module using python. This includes an easier way '
                'to generate latex tables and figures with the appropriate '
                'annotations (global, column, row and cell references).',
    long_description=README,
    url='https://www.hpvcentre.net',
    author='David Gómez',
    author_email='info@hpvcenter.net',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    install_requires=[
        # 'reportcompiler-ic-fetcher',
        'odictliteral',
        'plotnine',
        'fiona',
        'geopandas',
        'pyproj'
        'sphinx-autoapi',
        'setuptools',
        'sphinx',
        'autoapi',
        'sphinxcontrib-websupport'
    ],
)
