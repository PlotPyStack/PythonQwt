@echo off
setlocal
call %~dp0func SetPythonPath
call %~dp0func UseWinPython
python -m qwt.tests.__init__
call %~dp0func EndOfScript