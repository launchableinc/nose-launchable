current=`cat version`

read -p "Next version (current version: $current): " next
echo $next > version

./scripts/build.sh

twine upload --repository pypi dist/*
