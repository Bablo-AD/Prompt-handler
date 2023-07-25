from setuptools import setup, find_packages
with open("README.md", "r") as fh:
    long_description = fh.read()
with open("LICENSE", "r") as fg:
    license_val = fg.read()
setup(
    name="prompthandler",
    version="0.0.2",
    author="prasannan-robots",
    description="Token Management system for chatgpt and more. Keeps your prompt under token with summary support",
    install_requires=["openai","tiktoken"],
    packages=['prompthandler'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    license = license_val,
    long_description=long_description,      # Long description read from the the readme file
    long_description_content_type="text/markdown",
    keywords='openai chatgpt prompts summarizer handler summary token gpt-4'
)
