@echo off
set UNATTENDED=1
call build_doc.bat
call build_dist.bat
@echo:
@echo ==============================================================================
choice /t 5 /c yn /cs /d n /m "Do you want to upload packages to PyPI (y/n)?"
if errorlevel 2 goto :no
if errorlevel 1 goto :yes
:yes
@echo ==============================================================================
@echo:
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