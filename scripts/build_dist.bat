@echo off
cd %~dp0..\
if exist MANIFEST ( del /q MANIFEST )
if exist build ( rmdir /s /q build )
if exist dist ( rmdir /s /q dist )
call %~dp0func SetPythonPath
call %~dp0func UseWinPython
python setup.py sdist bdist_wheel --universal
python setup.py build sdist
call %~dp0func EndOfScript