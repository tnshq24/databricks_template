from setuptools import find_packages, setup
from UnnamedSlug import __version__

setup(
    name="UnnamedSlug",
    packages=find_packages(exclude=["tests", "tests.*"]),
    setup_requires=["wheel"],
    version=__version__,
    description="setting up databricks cicd template",
    author="Tanishq Singh",
)
