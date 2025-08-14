from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="akamai-usage-reporter",
    version="1.0.0",
    author="Akamai Usage Reporter",
    description="A CLI tool that analyzes Akamai account usage and generates Cloudflare migration checklists",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/elif-globaldots/akamai-usage-reporter",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "Topic :: System :: Networking :: Monitoring",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "akamai-usage-reporter=akamai_usage_reporter.__main__:main",
        ],
    },
    keywords="akamai, cloudflare, cdn, migration, cli, api",
    project_urls={
        "Bug Reports": "https://github.com/elif-globaldots/akamai-usage-reporter/issues",
        "Source": "https://github.com/elif-globaldots/akamai-usage-reporter",
        "Documentation": "https://github.com/elif-globaldots/akamai-usage-reporter#readme",
    },
)
