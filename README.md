[![Build Status](https://travis-ci.org/DoctorHayes/235CppStyle.svg?branch=master)](https://travis-ci.org/DoctorHayes/235CppStyle)
![GitHub Pipenv locked Python version](https://img.shields.io/github/pipenv/locked/python-version/DoctorHayes/235CppStyle)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://raw.githubusercontent.com/DoctorHayes/235CppStyle/master/LICENSE)

235CppStyle
===========

This is a Python web application that partially evaluates the coding style of students' .cpp and .h files for CSCI 235, a computer science course at [Charleston Southern University](http://www.csuniv.edu/).

This is a fork of [cppStyle](https://github.com/Bwolfing/cppstyle), used at the University of Michigan.

## Setup for Web Development

Currently, the app supports use with both Python 2.7.x and 3.x, but development is moving to 3.x.

* We recommend upgrading pip (the Python package manager) before installing the required Python packages.
  -  On Linux or macOS:  
     `pip install -U pip`
  - On Windows:  
    `python -m pip install -U pip`

* Setup and activate a virtual environment with pipenv (optional step)  
  1.  Install pipenv: `pip install pipenv`
  2.  Initialize the virtual environment: `pipenv install`
  3.  To activate this project's virtualenv, run `pipenv shell`.  
      Alternatively, run a command inside the virtualenv with `pipenv run`.
  4.  Exit the environment with `exit` when finished.

* Install dependencies (if not using pipenv) 
  `pip install -r requirements.txt`

* Launch the webapp locally  
  `python ./run.py`

* Run the application in debug mode (in Windows)  
  ```batch
  SET FLASK_APP=run.py
  SET FLASK_DEBUG=1
  python -m flask run
  ```

* Run the application in debug mode (in Linux)  
  ```shell
  export FLASK_APP=run.py
  export FLASK_DEBUG=1
  python -m flask run
  ```

## Run Regression Tests

* Install pytest.  
  `pip install -U pytest`
* Execute all the tests.  
  `pytest`
* To stop at first failed assertion.  
  `pytest -x`
* Example of running one specific test.  
  `pytest -k test_good_operator_spacing`