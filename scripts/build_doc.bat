@echo off
call %~dp0func SetPythonPath
call %~dp0func UseWinPython
set PATH=C:\Program Files\7-Zip;C:\Program Files (x86)\7-Zip;C:\Program Files\HTML Help Workshop;C:\Program Files (x86)\HTML Help Workshop;%PATH%
cd %~dp0..\
sphinx-build -b htmlhelp doc build\doc
hhc build\doc\PythonQwt.hhp
copy /y build\doc\PythonQwt.chm doc\_downloads
7z a doc\_downloads\PythonQwt.chm.zip doc\_downloads\PythonQwt.chm
move /y doc\PythonQwt.chm .
sphinx-build -b html doc build\doc
call %~dp0func EndOfScript