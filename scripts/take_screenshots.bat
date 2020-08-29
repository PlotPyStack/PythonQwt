@echo off
setlocal
call %~dp0func SetPythonPath
call %~dp0func UseWinPython
cd %~dp0..\
python qwt/tests/__init__.py --mode screenshots
call %~dp0func EndOfScript