"""Setup script for the meatball package."""

from setuptools import setup, find_packages

setup(
    name="meatball",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "streamlit>=1.24.0",
        "typing-extensions>=4.5.0",
    ],
    python_requires=">=3.8",
    author="Nathan Kundtz",
    description="A tool for practicing chord progressions",
    keywords="music, chords, practice, training",
    package_data={
        "meatball": [
            "static/js/*.js",
            "static/css/*.css",
        ],
    },
)
