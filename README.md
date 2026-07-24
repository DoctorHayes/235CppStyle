[![Python Tests](https://github.com/DoctorHayes/235CppStyle/actions/workflows/python-tests.yml/badge.svg)](https://github.com/DoctorHayes/235CppStyle/actions/workflows/python-tests.yml)
![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://raw.githubusercontent.com/DoctorHayes/235CppStyle/master/LICENSE)

235CppStyle
===========

This is a Python web application that partially evaluates the coding style of students' .cpp and .h files for CSCI 235, a computer science course at [Charleston Southern University](http://www.csuniv.edu/).

This is a fork of [cppStyle](https://github.com/Bwolfing/cppstyle), used at the University of Michigan.

Requires **Python 3.12+**. Dependencies are managed via `pyproject.toml` using standard Python packaging tools — no Pipenv or requirements.txt needed.

## Installation

First, create and activate a virtual environment (recommended):

```shell
python -m venv .venv

# Linux / macOS
source .venv/bin/activate

# Windows (CMD)
.venv\Scripts\activate
```

Then install the appropriate dependency set for your use case:

### CLI only (`run_local.py` / `run_local_for_parsing.py`)

Installs the core dependencies (`cpplint`, `pyparsing`) needed to grade files from the command line:

```shell
pip install -e .
```

### Web application (`run.py`)

Installs core dependencies plus Flask, Werkzeug, and Gunicorn:

```shell
pip install -e ".[web]"
```

### Development (tests + web)

Installs everything including `pytest`:

```shell
pip install -e ".[web,dev]"
```

## Running the Application

### Command-line grader

```shell
python ./run_local.py path/to/file.cpp
python ./run_local_for_parsing.py path/to/file.cpp
```

### Web application (local dev server)

```shell
python ./run.py
```

### Web application (debug mode — Windows)

```batch
SET FLASK_APP=run.py
SET FLASK_DEBUG=1
python -m flask run
```

### Web application (debug mode — Linux / macOS)

```shell
export FLASK_APP=run.py
export FLASK_DEBUG=1
python -m flask run
```

## Run Regression Tests

Install the `dev` extras (see above), then:

* Execute all the tests.  
  `pytest`
* Stop at the first failed assertion.  
  `pytest -x`
* Run one specific test.  
  `pytest -k test_good_operator_spacing`