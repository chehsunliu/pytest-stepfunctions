from pathlib import Path
from setuptools import setup, find_packages


setup(
    name="pytest-stepfunctions",
    version="0.0.1",
    author="Che-Hsun Liu",
    author_email="chehsunliu@gmail.com",
    description="A small description",
    long_description=Path("./README.md").read_text(),
    long_description_content_type="text/markdown",
    license="MIT",
    url="https://github.com/chehsunliu/pytest-stepfunctions",
    setup_requires=["setuptools_scm"],
    use_scm_version=True,
    packages=find_packages("src"),
    package_dir={"": "src"},
    install_requires=["pytest"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
