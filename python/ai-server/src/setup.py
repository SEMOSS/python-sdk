from setuptools import find_packages, setup
import os

# Read the contents of README.md if it exists
if os.path.exists("README.md"):
    with open("README.md", "r") as f:
        long_description = f.read()
else:
    long_description = "AI Server SDK - Python client SDK to connect to the AI Server."

setup(
    name="ai-server-sdk",
    version="0.0.20",
    packages=find_packages(),
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
