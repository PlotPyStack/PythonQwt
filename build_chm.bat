sphinx-build -b htmlhelp doc doctmp
"C:\Program Files\HTML Help Workshop\hhc.exe" doctmp\python-qwtdoc.hhp
"C:\Program Files (x86)\HTML Help Workshop\hhc.exe" doctmp\python-qwtdoc.hhp
copy doctmp\python-qwtdoc.chm .
rmdir /S /Q doctmp
pause