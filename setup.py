# setup.py

import pathlib
from setuptools import setup, find_packages

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# Long description pulled from the project README
long_description = (HERE / "README.md").read_text(encoding="utf-8")

setup(
    name="dwin_hmi_py",
    version="0.1.0",
    author="Oğuzhan Sezgin",
    description="Python library for controlling DWIN DGUS HMI modules over serial",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/oguzhans26/dwin_hmi_py",
    project_urls={
        "Documentation": "https://github.com/oguzhans26/dwin_hmi_py#readme",
        "Source": "https://github.com/oguzhans26/dwin_hmi_py",
        "Issue Tracker": "https://github.com/oguzhans26/dwin_hmi_py/issues",
    },
    license="MIT",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Embedded Systems",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent",
    ],
    keywords="dwin dgus hmi serial communication",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.6, <4",
    install_requires=[
        "pyserial>=3.4"
    ],
    include_package_data=True,
)
