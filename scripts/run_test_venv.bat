@echo off
REM ======================================================
REM Virtual environment test script
REM ======================================================
REM Licensed under the terms of the MIT License
REM Copyright (c) 2020 Pierre Raybaut
REM (see PythonQwt LICENSE file for more details)
REM ======================================================
setlocal
call %~dp0utils GetScriptPath SCRIPTPATH
set UNATTENDED=1
call %SCRIPTPATH%\build_dist
set PYTHONPATH=
call %FUNC% UseWinPython
call :TestEnv PyQt5
call :TestEnv PySide2
set UNATTENDED=
call %FUNC% EndOfScript
exit /B %ERRORLEVEL%

:TestEnv
call %FUNC% GetLibName LIBNAME
call %FUNC% ShowTitle "Testing in %~1-based Python virtual environment"
set VENVPATH=%SCRIPTPATH%\..\build\testenv
if exist %VENVPATH% ( rmdir /s /q %VENVPATH% )
python -m venv %VENVPATH%
call %VENVPATH%\Scripts\activate
python -m pip install --upgrade pip
pip install %~1
for %%f IN ("%SCRIPTPATH%\..\dist\%LIBNAME%-*.whl") DO ( pip install %%f )
call %VENVPATH%\Scripts\%LIBNAME%-tests --mode unattended
call %VENVPATH%\Scripts\deactivate
exit /B 0
