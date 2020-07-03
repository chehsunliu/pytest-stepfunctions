from pathlib import Path
from setuptools import setup, find_packages


setup(
    name="pytest-stepfunctions",
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
    entry_points={"pytest11": ["pytest-stepfunctions = pytest_stepfunctions.plugin"]},
    classifiers=[
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Development Status :: 1 - Planning",
        "Framework :: Pytest",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Software Development :: Testing",
    ],
    python_requires=">=3.6",
)
