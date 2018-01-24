[![Build Status](https://travis-ci.org/DoctorHayes/235CppStyle.svg?branch=master)](https://travis-ci.org/DoctorHayes/235CppStyle)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://raw.githubusercontent.com/DoctorHayes/235CppStyle/master/LICENSE)

235CppStyle
================

This is a Python web application partially evaluates the coding style of students' .cpp and .h files for CSCI 235, a computer science course at [Charleston Southern University](http://www.csuniv.edu/).

This is a fork of [cppStyle](https://github.com/Bwolfing/cppstyle), used at the University of Michigan.

## Setup for Web Development

Currently the app supports use with both Python 2.7 and 3.6.

* Download pip the package manager.  
  http://pip.readthedocs.org/en/latest/installing.html

* Download virtual environment:  
  `pip install virtualenv`

* Activate the virtual environment (optional step)  
  `virtualevn ENV`  
  In Windows: `ENV\Scripts\activate`  
  On Mac/Linux: `source ENV/bin/activate`

* Install Dependencies  
  `pip install -r requirements.txt` (Mac replace Scripts with bin)

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
  export FLASK_APP=main.py
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
* Example of running a one specific test.  
  `pytest test/regression_test.py -k test_good_operator_spacing`