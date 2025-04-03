"""
Setup configuration for pychapi package
"""
from setuptools import setup, find_packages

setup(
    name="pychapi",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "aiohttp>=3.9.0",
        "pydantic>=2.0.0",
    ],
    python_requires=">=3.9",
) 