import chatlib
from setuptools import setup

setup(
    name="pychatlib",
    version=chatlib.__version__,
    description="Provides functionality to read messaging/chat application exports.",
    url="https://github.com/lahdjirayhan/pychatlib",
    license='BSD 3-clause',
    author=chatlib.__author__,
    packages=['chatlib'],
    install_requires=['pydateinfer']
)
