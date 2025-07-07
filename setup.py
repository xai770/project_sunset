from setuptools import setup, find_packages

setup(
    name="sandy",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pandas",
        "openpyxl",
        "requests",
    ]
)
