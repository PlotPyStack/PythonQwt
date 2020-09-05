@echo off
REM ======================================================
REM Screenshots update script
REM ======================================================
REM Licensed under the terms of the MIT License
REM Copyright (c) 2020 Pierre Raybaut
REM (see LICENSE file for more details)
REM ======================================================
setlocal
call %~dp0utils GetScriptPath SCRIPTPATH
call %FUNC% SetPythonPath
call %FUNC% UseWinPython
cd %SCRIPTPATH%\..\
python qwt/tests/__init__.py --mode screenshots
call %FUNC% EndOfScript