@echo off
REM Update Python
pip install --upgrade pip
pip install --upgrade setuptools
REM Install required libraries
pip install flask neuralintents sqlalchemy opencv-python-headless
pause
