from setuptools import setup, find_packages

setup(
    name="code_agent",
    version="0.1.0",
    description="A multi-agent system that automates software development workflows",
    author="Miles Exner",
    author_email="flyingback@me.com",
    packages=find_packages(),
    install_requires=[
        "smolagents>=0.1.0",
        "pygithub>=1.58.0",
        "python-dotenv>=1.0.0",
        "pytest>=7.0.0",
        "black>=23.0.0",
        "tqdm>=4.65.0",
    ],
    entry_points={
        "console_scripts": [
            "code-agent=code_agent.cli:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
) 
