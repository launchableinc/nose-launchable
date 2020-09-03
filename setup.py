from setuptools import setup, find_packages
from os import path


def read(file):
    return open(path.join(path.dirname(__file__), file)).read()


def _requirements(file):
    return open(file).read().splitlines()


version = '0.0.2'

setup(
    name='nose-reorder',
    version=version,
    url='https://github.com/launchableinc/nose-reorder',
    author='Launchable team',
    author_email=' info@launchableinc.com',
    description='A nose plugin to reorder tests by likelihood of failure',
    long_description=read("README.rst"),
    packages=find_packages(),
    install_requires=_requirements('requirements.txt'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
    ],
    entry_points={
        'nose.plugins.0.10': [
            'reorder = reorder:Reorder'
        ],
    },
)
