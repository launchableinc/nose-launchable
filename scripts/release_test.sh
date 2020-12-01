current=`cat nose_launchable/version.py`

read -p "Next version (current version: $current): " next
echo "__version__ = '$next'" > nose_launchable/version.py

./scripts/build.sh

twine upload --repository testpypi dist/*
