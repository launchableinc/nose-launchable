current=`cat launchable/version.py`

read -p "Next version (current version: $current): " next
echo "__version__ = '$next'" > launchable/version.py

./scripts/build.sh

git commit -am "Bumps up to v$next"
git tag "v$next"

git push origin main
git push origin --tags

twine upload --repository pypi dist/*
