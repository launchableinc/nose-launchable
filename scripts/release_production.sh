current=`cat launchable/version.py`

read -p "Next version (current version: $current): " next
echo "__version__ = '$next'" > launchable/version.py

./scripts/build.sh

twine upload --repository pypi dist/*
