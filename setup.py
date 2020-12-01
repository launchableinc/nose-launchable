from os import path

from setuptools import setup, find_packages

from nose_launchable.version import __version__


def _read(file):
    return open(path.join(path.dirname(__file__), file)).read()


def _requirements(file):
    return open(file).read().splitlines()


setup(
    name='nose-launchable',
    version=__version__,
    url='https://github.com/launchableinc/nose-launchable',
    author='Launchable team',
    author_email=' info@launchableinc.com',
    description='A nose plugin to interact with Launchable API',
    long_description=_read("README.rst"),
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
            'nose_launchable = nose_launchable:Launchable'
        ],
    },
)
