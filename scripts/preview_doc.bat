@echo off
REM ======================================================
REM Documentation build script
REM ======================================================
REM Licensed under the terms of the MIT License
REM Copyright (c) 2020 Pierre Raybaut
REM (see LICENSE file for more details)
REM ======================================================
call %~dp0utils GetScriptPath SCRIPTPATH
call %FUNC% SetPythonPath
call %FUNC% UseWinPython
cd %SCRIPTPATH%\..\
if exist build\doc ( rmdir /s /q build\doc )
sphinx-build -b html doc build\doc
start build\doc\index.html
call %FUNC% EndOfScript