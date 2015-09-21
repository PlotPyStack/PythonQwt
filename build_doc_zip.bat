sphinx-build -b html doc doctmp
cd doctmp
7z a -r ..\doc.zip *.*
cd ..
rmdir /S /Q doctmp