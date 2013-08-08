from setuptools import setup
import demands

setup(
    name=demands.__name__,
    version=demands.__version__,
    description=demands.__doc__, 
    author='Yola',
    author_email='engineers@yola.com',
    license='MIT (Expat)',
    url=demands.__url__,
    packages=['demands'],
    install_requires=['requests >= 1.0.0, < 2.0.0']
)
