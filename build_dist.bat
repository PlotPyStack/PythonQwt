del MANIFEST
rmdir /S /Q build
rmdir /S /Q dist
python setup.py build bdist_wininst --plat-name=win32
python setup.py build bdist_wininst --plat-name=win-amd64
python setup.py sdist bdist_wheel --universal
python setup.py build sdist