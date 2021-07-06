from setuptools import setup

with open("README.md") as f:
    long_description = f.read()


setup(
    name="prefixdate",
    version="0.3.0",
    description="Formatting utility for international postal addresses",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pudo/prefixdate",
    author="Friedrich Lindenberg",
    author_email="friedrich@pudo.org",
    license="MIT",
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
    package_data={"prefixdate": ["py.typed"]},
    include_package_data=True,
    scripts=[],
    install_requires=[],
    zip_safe=False,
    extras_require={
        "dev": [
            "pytest",
            "pytest-cov",
            "mypy",
            "bump2version",
            "wheel>=0.29.0",
            "twine",
        ],
    },
)
