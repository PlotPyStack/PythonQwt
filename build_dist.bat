del MANIFEST
rmdir /S /Q build
rmdir /S /Q dist
set PYTHONPATH=%cd%
python setup.py sdist bdist_wheel --universal
python setup.py build sdist