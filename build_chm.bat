sphinx-build -b htmlhelp doc doctmp
"C:\Program Files\HTML Help Workshop\hhc.exe" doctmp\python-qwt.hhp
"C:\Program Files (x86)\HTML Help Workshop\hhc.exe" doctmp\python-qwt.hhp
copy doctmp\python-qwt.chm .
7z a python-qwt.chm.zip python-qwt.chm
del doctmp\python-qwt.chm
del doc.zip
sphinx-build -b html doc doctmp
cd doctmp
7z a -r ..\doc.zip *.*
cd ..
rmdir /S /Q doctmp
del python-qwt.chm.zip