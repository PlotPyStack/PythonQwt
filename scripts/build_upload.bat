@echo off
REM ======================================================
REM Package build and upload script
REM ======================================================
REM Licensed under the terms of the MIT License
REM Copyright (c) 2020 Pierre Raybaut
REM (see LICENSE file for more details)
REM ======================================================
call %~dp0utils GetScriptPath SCRIPTPATH
set UNATTENDED=1
call %SCRIPTPATH%\clean_up.bat
@REM call %SCRIPTPATH%\build_doc.bat
call %SCRIPTPATH%\build_dist.bat
@echo:
@echo ==============================================================================
choice /t 5 /c yn /cs /d n /m "Do you want to upload packages to PyPI (y/n)?"
if errorlevel 2 goto :no
if errorlevel 1 goto :yes
:yes
@echo ==============================================================================
@echo:
cd %SCRIPTPATH%\..
twine upload dist/*
GOTO :continue
:no
@echo:
@echo Warning: Packages were not uploaded to PyPI
:continue
@echo:
@echo ==============================================================================
@echo:
@echo End of script
pause