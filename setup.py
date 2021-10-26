from os.path import join, dirname

from pkg_resources import parse_requirements
from setuptools import setup


def read_requirements(filename):
    path = join(dirname(__file__), filename)
    return [str(r) for r in parse_requirements(open(path, 'r'))]


setup(
    install_requires=read_requirements("requirements.txt"),
    tests_require=read_requirements("requirements_tests.txt"),
)
