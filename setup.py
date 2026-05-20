"""
Setup configuration for MathSearch package.
Allows installation via: pip install -e .
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="mathsearch",
    version="1.0.0",
    author="Search Engine Contributors",
    description="An advanced mathematical search engine with BM25 ranking and semantic re-ranking",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/Search-Engine",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Education",
        "Topic :: Education :: Testing",
        "Topic :: Internet :: WWW/HTTP :: Indexing/Search",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "Flask==2.3.3",
        "requests==2.31.0",
        "beautifulsoup4==4.12.2",
        "numpy==1.24.3",
        "pyspellchecker==0.7.0",
        "sentence-transformers==2.2.2",
        "torch==2.0.1",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "black>=23.0",
            "flake8>=6.0",
            "mypy>=1.0",
        ],
    },
)
