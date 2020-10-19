import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="gdpys",
    version="0.0.1",
    author="RealistikDash",
    description=(
        "GDPyS is a Python based Geometry Dash server, it has many unique features including plugins and custom magic and awarded sections. What makes GDPyS better than other alternatives is because of the speed. GDPyS runs much faster than other alternatives and offers many configuration options like Cheatless AntiCheat and more."
    ),
    license="MIT",
    packages=["gdpys"],
    long_description=read("README.md"),
    project_urls={
        "Documentation": "https://gdpys.readthedocs.io/en/latest",
        "Issue tracker": "https://github.com/RealistikDash/GDPyS/issues",
    },
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Operating System :: OS Independent",
    ],
    entry_points={"gdpys": ["gdpys = gdpys.__main__:main"]},
)
