""" Module for installing module as pip package """
import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

os.chdir(
    os.path.normpath(
        os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='reportcompiler-ic-tools',
    version='0.3.0',
    packages=find_packages('.', exclude=['test']),
    include_package_data=True,
    package_data={'reportcompiler_ic_tools': ['data/*']},
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
        'reportcompiler-ic-fetcher',
        'odictliteral',
        'plotnine',  # Currently requires development version
        'fiona',
        'geopandas',
        'pyproj'
    ],
)
