[![Build Status](https://travis-ci.org/DoctorHayes/235CppStyle.svg?branch=master)](https://travis-ci.org/DoctorHayes/235CppStyle)
[![license](https://img.shields.io/github/license/DoctorHayes/235CppStyle.svg)]()

235CppStyle
================

This is a web application that *will* aid in evaluating the coding style of students' .cpp and .h files for CSCI 235, a computer science course at [Charleston Southern University](http://www.csuniv.edu/).

This is a fork of [cppStyle](https://github.com/Bwolfing/cppstyle), used at the University of Michigan.

## Setup for Web Development

* Download pip the package manager.  
  http://pip.readthedocs.org/en/latest/installing.html

* Download virtual environment:  
  `pip install virtualenv`

* Activate the virtual environment  
  `virtualevn ENV`  
  In Windows: `ENV\Scripts\activate`  
  On Mac/Linux: `source ENV/bin/activate`

* Install Dependencies  
  `ENV\Scripts\pip install -r requirements.txt` (Mac replace Scripts with bin)

* Launch the webapp locally  
  From root, run `./run.py`

## Run Regression Tests

* Install pytest.  
  `pip install -U pytest`
* Execute the tests.  
  `pytest`