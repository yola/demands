from setuptools import setup

setup(
    name='demands',
    version='0.1.0',
    description='Base HTTP service client',
    url='https://github.com/yola/demands',
    packages=['demands'],
    install_requires=['requests < 1.0.0']
)
