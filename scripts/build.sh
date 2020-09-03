pip install wheel twine

rm -f -r nose_reorder.egg-info/ dist/ build/
python setup.py sdist
python setup.py bdist_wheel

pandoc --from markdown --to rst README.md -o README.rst
