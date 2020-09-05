@echo off
REM ======================================================
REM Documentation build script
REM ======================================================
REM Licensed under the terms of the MIT License
REM Copyright (c) 2020 Pierre Raybaut
REM (see LICENSE file for more details)
REM ======================================================
call %~dp0utils GetScriptPath SCRIPTPATH
call %FUNC% GetLibName LIBNAME
call %FUNC% SetPythonPath
call %FUNC% UseWinPython
set PATH=C:\Program Files\7-Zip;C:\Program Files (x86)\7-Zip;C:\Program Files\HTML Help Workshop;C:\Program Files (x86)\HTML Help Workshop;%PATH%
cd %SCRIPTPATH%\..\
sphinx-build -b htmlhelp doc build\doc
hhc build\doc\%LIBNAME%.hhp
copy /y build\doc\%LIBNAME%.chm doc\_downloads
7z a doc\_downloads\%LIBNAME%.chm.zip doc\_downloads\%LIBNAME%.chm
move /y doc\%LIBNAME%.chm .
sphinx-build -b html doc build\doc
call %FUNC% EndOfScript