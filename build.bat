rmdir /S /Q build
rmdir /S /Q dist
python setup.py build sdist
python setup.py sdist bdist_wheel --universal
pause