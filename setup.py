from chatlib import (
    __version__ as version,
    __author__ as author
)
from setuptools import setup
from pathlib import Path

readme_path = Path(__file__).parent.joinpath("README.md")
with open(readme_path) as f:
    readme_contents = f.read()

setup(
    name="pychatlib",
    version=version,
    description="Provides functionality to read messaging/chat application exports.",
    url="https://github.com/lahdjirayhan/pychatlib",
    license='BSD 3-clause',
    author=author,
    packages=['chatlib'],
    long_description = readme_contents,
    long_description_content_type = "text/markdown"
)
