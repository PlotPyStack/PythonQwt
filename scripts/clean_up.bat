@echo off
REM ======================================================
REM Clean up repository
REM ======================================================
REM Licensed under the terms of the MIT License
REM Copyright (c) 2020 Pierre Raybaut
REM (see PythonQwt LICENSE file for more details)
REM ======================================================
call %~dp0utils GetScriptPath SCRIPTPATH
call %FUNC% GetLibName LIBNAME
cd %SCRIPTPATH%\..\
if exist MANIFEST ( del /q MANIFEST )
if exist build ( rmdir /s /q build )
if exist dist ( rmdir /s /q dist )
del /s /q *.pyc
FOR /d /r %%d IN ("__pycache__") DO @IF EXIST "%%d" rd /s /q "%%d"
