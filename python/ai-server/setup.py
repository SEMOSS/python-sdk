from setuptools import find_packages, setup
import os

if os.path.exists("README.md"):
    with open("README.md", "r", encoding="utf-8") as f:
        long_description = f.read()
else:
    long_description = "AI Server SDK - Python client SDK to connect to the AI Server."

setup(
    name="ai-server-sdk",
    version="0.0.23",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "requests",
        "pandas",
        "jsonpickle",
    ],
    extras_require={"full": ["langchain", "langchain-community"]},
    author="Thomas Trankle, Maher Khalil, Ryan Weiler",
    description="Utility package to connect to AI Server instances.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
)
