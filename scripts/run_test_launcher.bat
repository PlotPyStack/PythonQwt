@echo off
REM ======================================================
REM Test launcher script
REM ======================================================
REM Licensed under the terms of the MIT License
REM Copyright (c) 2020 Pierre Raybaut
REM (see LICENSE file for more details)
REM ======================================================
setlocal
call %~dp0utils GetScriptPath SCRIPTPATH
call %FUNC% SetPythonPath
call %FUNC% UseWinPython
python -m qwt.tests.__init__
call %FUNC% EndOfScript