@echo off
REM ======================================================
REM Package build script
REM ======================================================
REM Licensed under the terms of the MIT License
REM Copyright (c) 2020 Pierre Raybaut
REM (see LICENSE file for more details)
REM ======================================================
call %~dp0utils GetScriptPath SCRIPTPATH
call %FUNC% GetLibName LIBNAME
cd %SCRIPTPATH%\..\
if exist MANIFEST ( del /q MANIFEST )
if exist build ( rmdir /s /q build )
if exist dist ( rmdir /s /q dist )
call %FUNC% SetPythonPath
call %FUNC% UseWinPython
python setup.py sdist bdist_wheel --universal
python setup.py build sdist
rmdir /s /q %LIBNAME%.egg-info
call %FUNC% EndOfScript