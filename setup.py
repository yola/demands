from setuptools import setup

setup(
    name='demands',
    version='1.0.4',
    description='Base HTTP service client',
    author='Yola',
    author_email='engineers@yola.com',
    license='MIT (Expat)',
    url='https://github.com/yola/demands',
    packages=['demands'],
    install_requires=['requests >= 1.0.0, < 2.0.0']
)
