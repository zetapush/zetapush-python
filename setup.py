import os
from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name = 'zetapush_python',
    version = "0.1.0",
    author = "Damien",
    author_email = "FIXME",
    description = "Zetapush Python client",
    license = "MIT",
    packages = find_packages(),
    package_data={
    },
    entry_points={ },
    install_requires = requirements
)