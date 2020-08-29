@echo off
setlocal
set UNATTENDED=1
call %~dp0build_dist
set PYTHONPATH=
call %~dp0func UseWinPython
call :TestEnv PyQt5
call :TestEnv PySide2
set UNATTENDED=
call %~dp0func EndOfScript
exit /B %ERRORLEVEL%

:TestEnv
call %~dp0func ShowTitle "Testing in %~1-based Python virtual environment"
set VENVPATH=cd %~dp0..\build\testenv
python -m venv %VENVPATH%
call %VENVPATH%\Scripts\activate
pip install %~1
for %%f IN ("%~dp0..\dist\PythonQwt-*.whl") DO ( pip install %%f )
call %VENVPATH%\Scripts\PythonQwt-tests-py3 --mode unattended
call %VENVPATH%\Scripts\deactivate
exit /B 0