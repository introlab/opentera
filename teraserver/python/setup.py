import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="opentera",  # Replace with your own username
    version="1.0.2",
    author="Dominic Létourneau, Simon Brière",
    author_email="dominic.letourneau@usherbrooke.ca, simon.briere@usherbrooke.ca",
    description="OpenTera base package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/introlab/opentera",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
