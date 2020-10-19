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
    packages=["gdpys"],
    long_description=read("README.md"),
)
