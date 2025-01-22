import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("env/requirements.txt", "r", encoding="utf-8") as f:
    requirements = f.readlines()

setuptools.setup(
    name="opentera",
    version="1.3.1",
    author="Dominic Létourneau, Simon Brière",
    author_email="dominic.letourneau@usherbrooke.ca, simon.briere@usherbrooke.ca",
    description="OpenTera base package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/introlab/opentera",
    packages=setuptools.find_packages(),
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.10',
)
