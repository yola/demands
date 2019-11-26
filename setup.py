import re

from setuptools import setup

with open('demands/__init__.py') as init_py:
    metadata = dict(re.findall("__([a-z]+)__ = '([^']+)'", init_py.read()))

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
    install_requires=[
        'requests >= 2.4.2, < 3.0.0',
        'six',
    ],
    test_suite='nose.collector',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries',
    ],
)
