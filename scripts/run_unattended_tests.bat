@echo off
REM ======================================================
REM Unattended test script
REM ======================================================
REM Licensed under the terms of the MIT License
REM Copyright (c) 2020 Pierre Raybaut
REM (see LICENSE file for more details)
REM ======================================================
setlocal
call %~dp0utils GetScriptPath SCRIPTPATH
call %FUNC% SetPythonPath
cd %SCRIPTPATH%\..\

if not defined WINPYDIRBASE ( goto :no )
choice /t 5 /c yn /cs /d n /m "Do you want to run tests only from %WINPYDIRBASE% (y/n)?"
if errorlevel 2 goto :no
:yes
call %WINPYDIRBASE%\scripts\env.bat
python qwt/tests/__init__.py --mode unattended
pause
exit /B %ERRORLEVEL%
:no
for /f %%f in ('dir /b c:\w*') do (call :test %%f)
pause
exit /B %ERRORLEVEL%

:test
set ENV=C:\%~1\scripts\env.bat
if exist %ENV% (
    @echo:
    @echo ************************** Testing with %~1 **************************
    @echo:
    call %ENV%
    python -m qwt.tests.__init__ --mode unattended
    )
exit /B 0