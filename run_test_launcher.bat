@echo off
setlocal
set PYTHONPATH=%cd%
if defined WINPYDIRBASE (
    call %WINPYDIRBASE%\scripts\env.bat
    @echo ==============================================================================
    @echo:
    @echo Using WinPython from %WINPYDIRBASE%
    @echo:
    @echo ==============================================================================
    @echo:
    )
python -m qwt.tests.__init__