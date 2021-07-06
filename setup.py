from setuptools import setup

with open("README.md") as f:
    long_description = f.read()


setup(
    name="prefixdate",
    version="0.1.0",
    description="Formatting utility for international postal addresses",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pudo/prefixdate",
    author="Friedrich Lindenberg",
    author_email="friedrich@pudo.org",
    license="MIT",
    include_package_data=True,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent",
    ],
    keywords="date, partial date, iso8601, rfc3339",
    packages=["prefixdate"],
    scripts=[],
    install_requires=[],
    extras_require={
        "dev": [
            "pytest",
            "pytest-cov",
            "bump2version",
            "wheel>=0.29.0",
            "twine",
        ],
    },
)
