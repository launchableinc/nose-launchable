./scripts/bumps_up.sh
./scripts/build.sh

git commit -am "Bumps up to v$next"
git tag "v$next"

git push upstream main
git push upstream --tags

twine upload --repository pypi dist/*
