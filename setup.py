from setuptools import setup

setup(
    name="235CppStyle",
    description="Charleston Southern University CSCI 235 style grader.",
    install_requires=open("requirements.txt", "r").readlines(),
    packages=["235CppStyle"],
    package_data={"235CppStyle": ["rubric.ini"]},
    scripts=["bin/235CppStyle"],
    test_suite="235CppStyle.test"
)
