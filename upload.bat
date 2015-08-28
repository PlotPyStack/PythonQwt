rmdir /S /Q build
rmdir /S /Q dist
python setup.py build sdist upload
python setup.py sdist bdist_wheel --universal upload
pause