current=`cat nose_launchable/version.py`

read -p "Next version (current version: $current): " next
echo "__version__ = '$next'" > nose_launchable/version.py

./scripts/build.sh

git commit -am "Bumps up to v$next"
git tag "v$next"

git push upstream main
git push upstream --tags

twine upload --repository pypi dist/*
