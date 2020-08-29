REM Utilities for deployment, test and build scripts
@echo off
call:%*
goto Exit

:SetPythonPath
set PYTHONPATH=%~dp0..
goto:eof

:UseWinPython
if defined WINPYDIRBASE (
    call %WINPYDIRBASE%\scripts\env.bat
    call :ShowTitle "Using WinPython from %WINPYDIRBASE%"
    )
goto:eof

:ShowTitle
@echo:
@echo ========= %~1 =========
@echo:
goto:eof

:EndOfScript
@echo:
@echo **********************************************************************************
@echo:
if not defined UNATTENDED (
    @echo End of script
    pause
    )
goto:eof

:Exit
exit /b