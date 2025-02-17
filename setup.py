import os

from setuptools import setup

base_path = os.path.abspath(os.path.dirname(__file__))

requirements = []
with open("requirements.txt") as f:
    requirements = f.read().splitlines()

readme = ""
with open("README.md") as f:
    readme = f.read()

setup(
    name="DeeperSeek",
    author="Sxvxge",
    url="https://github.com/theAbdoSabbagh/DeeperSeek",
    project_urls={
        "Documentation": "https://github.com/theAbdoSabbagh/DeeperSeek/blob/main/README.md",
        "Issue tracker": "https://github.com/theAbdoSabbagh/DeeperSeek/issues",
        "Changelog": "https://github.com/theAbdoSabbagh/DeeperSeek/blob/main/CHANGELOG.md",
    },
    version="0.1.4",
    packages=["DeeperSeek", "DeeperSeek/internal"],
    # py_modules=["DeeperSeek"],
    license="GPL-3.0 license",
    description="An unofficial Python wrapper for DeepSeek API",
    long_description=readme,
    long_description_content_type="text/markdown",
    include_package_data=True,
    install_requires=requirements,
    python_requires=">=3.8.0",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
        "Typing :: Typed",
    ],
)
