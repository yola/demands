from setuptools import setup

exec(open('demands/__meta__.py').read())

setup(
    name='demands',
    version=__version__,  # NOQA
    description=__doc__,
    author='Yola',
    author_email='engineers@yola.com',
    license='MIT (Expat)',
    url='https://github.com/yola/demands',
    packages=['demands'],
    install_requires=['requests >= 1.0.0, < 2.0.0']
)
