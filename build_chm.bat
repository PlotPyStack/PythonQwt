sphinx-build -b htmlhelp doc doctmp
"C:\Program Files\HTML Help Workshop\hhc.exe" doctmp\PythonQwt.hhp
"C:\Program Files (x86)\HTML Help Workshop\hhc.exe" doctmp\PythonQwt.hhp
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