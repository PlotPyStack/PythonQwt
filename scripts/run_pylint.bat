@echo off
REM This script was derived from PythonQwt project
REM ======================================================
REM Run pylint analysis
REM ======================================================
REM Licensed under the terms of the MIT License
REM Copyright (c) 2020 Pierre Raybaut
REM (see PythonQwt LICENSE file for more details)
REM ======================================================
setlocal
call %~dp0utils GetScriptPath SCRIPTPATH
call %FUNC% GetModName MODNAME
call %FUNC% SetPythonPath
set PYLINT_ARG=%*
if "%PYLINT_ARG%"=="" set PYLINT_ARG=--disable=fixme
%PYTHON% -m pylint --rcfile=%SCRIPTPATH%\..\.pylintrc %PYLINT_ARG% %MODNAME%
call %FUNC% EndOfScript