@echo off

setlocal
set PYTHONPATH=%cd%
set TEST_UNATTENDED=1

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