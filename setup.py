import os
from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name = 'zetapush_python',
    version = "0.1.2",
    author = "Damien Le Dantec",
    author_email = "damien.le-dantec@zetapush.com",
    description = "Zetapush Python SDK",
    license = "MIT",
    packages = find_packages(),
    package_data={
    },
    entry_points={ },
    install_requires = requirements,
    include_package_data=True
)
