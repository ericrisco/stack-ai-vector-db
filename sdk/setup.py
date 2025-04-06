from setuptools import setup, find_packages

setup(
    name="stack-ai-vector-db",
    version="0.1.0",
    description="Python SDK for Stack AI Vector Database",
    author="Eric Risco de la Torre",
    author_email="erisco@icloud.com",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.0",
        "pydantic>=1.8.0",
        "uuid>=1.30",
    ],
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
) 