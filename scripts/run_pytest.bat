@echo off
REM This script was derived from PythonQwt project
REM ======================================================
REM Run pytest script
REM ======================================================
REM Licensed under the terms of the MIT License
REM Copyright (c) 2020 Pierre Raybaut
REM (see PythonQwt LICENSE file for more details)
REM ======================================================
setlocal enabledelayedexpansion
call %~dp0utils GetScriptPath SCRIPTPATH
call %FUNC% GetModName MODNAME
call %FUNC% SetPythonPath

:: Iterate over all directories in the grandparent directory
:: (WinPython base directories)
call %FUNC% GetPythonExeGrandParentDir DIR0
for /D %%d in ("%DIR0%*") do (
    set WINPYDIRBASE=%%d
    call !WINPYDIRBASE!\scripts\env.bat
    echo Running pytest from "%%d":
    pytest --ff -q
    echo ----
)
call %FUNC% EndOfScript
