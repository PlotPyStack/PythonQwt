@echo off

setlocal
set PYTHONPATH=%cd%
set TEST_UNATTENDED=1

if not defined WINPYDIRBASE ( goto :no )

choice /t 5 /c yn /cs /d n /m "Do you want to run tests only from %WINPYDIRBASE% (y/n)?"
if errorlevel 2 goto :no

:yes
call %WINPYDIRBASE%\scripts\env.bat
python -m qwt.tests.__init__
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
    python -m qwt.tests.__init__
    )
exit /B 0