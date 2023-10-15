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

@REM Removing files/directories related to Python/doc build process
if exist %LIBNAME%.egg-info ( rmdir /s /q %LIBNAME%.egg-info )
if exist MANIFEST ( del /q MANIFEST )
if exist build ( rmdir /s /q build )
if exist dist ( rmdir /s /q dist )
if exist doc\_build ( rmdir /s /q doc\_build )

@REM Removing files produced by tests
del *.h5
del *.json
del *.pickle

@REM Removing cache files/directories related to Python execution
del /s /q *.pyc 1>nul 2>&1
del /s /q *.pyo 1>nul 2>&1
FOR /d /r %%d IN ("__pycache__") DO @IF EXIST "%%d" rd /s /q "%%d"

@REM Removing directories related to public repository upload
set TEMP=%SCRIPTPATH%\..\..\%LIBNAME%_temp
set PUBLIC=%SCRIPTPATH%\..\..\%LIBNAME%_public
if exist %TEMP% ( rmdir /s /q %TEMP% )
if exist %PUBLIC% ( rmdir /s /q %PUBLIC% )

@REM Removing files/directories related to Coverage
if exist .coverage ( del /q .coverage )
if exist coverage.xml ( del /q coverage.xml )
if exist htmlcov ( rmdir /s /q htmlcov )
del /q .coverage.* 1>nul 2>&1
if exist sitecustomize.py ( del /q sitecustomize.py )