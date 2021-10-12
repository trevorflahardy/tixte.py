import pathlib
from setuptools import setup

HERE = pathlib.Path(__file__).parent

README = (HERE / "README.md").read_text()

VERSION = "0.0.6"

requirements = ['aiohttp>=3.6.0,<3.8.0']

setup(
    author="Iced Chai",
    name="tixte",
    description="The async wrapper for the Tixte API.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/NextChai/Tixte",
    project_urls = {
        'Report a Bug': 'https://github.com/NextChai/Tixte/issues',
        "Contribute": 'https://github.com/NextChai/Tixte/pulls'
    },
    version=VERSION,
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    packages=["tixte"],
    include_package_data=True,
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "square=square.__main__:main",
        ]
    },
)   