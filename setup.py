from setuptools import setup

setup(
	# Application name:
    name="235CppStyle",

    # Version number (initial):
    version="0.1.0",

    # Details
    description="Charleston Southern University CSCI 235 style grader.",
    long_description=open("README.md").read(),

    # Dependent packages (distributions)
    install_requires=open("requirements.txt", "r").readlines(),

    # Packages
    packages=["app"],
    package_data={"235CppStyle": ["rubric.ini"]},
    scripts=[],
    test_suite="235CppStyle.test"
)
