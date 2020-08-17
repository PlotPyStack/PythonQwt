@echo off
if defined WINPYDIRBASE (
    call %WINPYDIRBASE%\scripts\env.bat
    @echo ==============================================================================
    @echo:
    @echo Using WinPython from %WINPYDIRBASE%
    @echo:
    @echo ==============================================================================
    @echo:
    )
del MANIFEST
rmdir /S /Q build
rmdir /S /Q dist
set PYTHONPATH=%cd%
python setup.py sdist bdist_wheel --universal
python setup.py build sdist
@echo:
@echo ==============================================================================
@echo:
if not defined UNATTENDED (
    @echo End of script
    pause
    )