%PYTHON_EXE% bootstrap.py
CHOICE /T 20 /C w /D w
bin\buildout
bin\docpy setup.py sdist
bin\nosetests --with-xunit --with-cov --cov=configurator --cov-report=xml --cov-report=html