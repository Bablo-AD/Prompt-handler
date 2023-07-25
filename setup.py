from setuptools import setup, find_packages
setup(
    name="prompthandler",
    version="0.0.1",
    author="prasannan-robots",
    description="Token Management system for chatgpt and more. Keeps your prompt under token with summary support",
    install_requires=["openai","tiktoken"],
    packages=['prompthandler'],
    keywords='openai chatgpt prompts summarizer handler summary token gpt-4'
)
