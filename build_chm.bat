sphinx-build -b htmlhelp doc doctmp
"C:\Program Files\HTML Help Workshop\hhc.exe" doctmp\qwtdoc.hhp
"C:\Program Files (x86)\HTML Help Workshop\hhc.exe" doctmp\qwtdoc.hhp
copy doctmp\qwtdoc.chm .
rmdir /S /Q doctmp
pause