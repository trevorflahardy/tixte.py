import pathlib
import re

from setuptools import setup

here = pathlib.Path(__file__).parent
readme = (here / "README.md").read_text()

requirements = []
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

version = ''
with open('tixte/__init__.py') as f:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE).group(1)

extras_require = {
    'docs': [
        'sphinx==4.4.0',
        'sphinxcontrib_trio==1.1.2',
        'sphinxcontrib-websupport',
        'typing-extensions',
    ],
    'test': ['pytest', 'pytest-asyncio', 'pytest-cov', 'async-timeout'],
    'speed': [
        'orjson',
    ],
}

setup(
    author='NextChai',
    name='tixte.py',
    description='The async wrapper for the Tixte API.',
    long_description=readme,
    long_description_content_type='text/markdown',
    url='https://github.com/NextChai/Tixte',
    project_urls={
        'Report a Bug': 'https://github.com/NextChai/Tixte/issues',
        "Contribute": 'https://github.com/NextChai/Tixte/pulls',
    },
    version=version,
    license='MIT',
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    packages=['tixte'],
    include_package_data=True,
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "square=square.__main__:main",
        ]
    },
    extras_require=extras_require,
)
