@echo off
set FUNC=%0
call:%*
goto Exit

REM ======================================================
REM Utilities for deployment, test and build scripts
REM ======================================================
REM Licensed under the terms of the MIT License
REM Copyright (c) 2020 Pierre Raybaut
REM (see LICENSE file for more details)
REM ======================================================

:GetScriptPath
set _tmp_=%~dp0
if %_tmp_:~-1%==\ set %1=%_tmp_:~0,-1%
EXIT /B 0

:GetLibName
pushd %~dp0..
for %%I in (.) do set %1=%%~nxI
popd
goto:eof

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