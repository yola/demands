import re

from setuptools import setup

init_py = open('demands/__init__.py').read()
metadata = dict(re.findall("__([a-z]+)__ = '([^']+)'", init_py))

with open('README.rst') as readme_file:
    readme = readme_file.read()

setup(
    name='demands',
    version=metadata['version'],
    description=metadata['doc'],
    long_description=readme,
    author='Yola',
    author_email='engineers@yola.com',
    license='MIT (Expat)',
    url=metadata['url'],
    packages=['demands'],
    install_requires=['requests >= 2.4.2, < 3.0.0']
)
