@echo off
set PATH=C:\Program Files\7-Zip;C:\Program Files (x86)\7-Zip;C:\Program Files\HTML Help Workshop;C:\Program Files (x86)\HTML Help Workshop;%PATH%
set PYTHONPATH=%cd%
sphinx-build -b htmlhelp doc doctmp
hhc doctmp\PythonQwt.hhp
copy doctmp\PythonQwt.chm .
7z a PythonQwt.chm.zip PythonQwt.chm
del doctmp\PythonQwt.chm
del doc.zip
sphinx-build -b html doc doctmp
cd doctmp
7z a -r ..\doc.zip *.*
cd ..
rmdir /S /Q doctmp
del PythonQwt.chm.zip