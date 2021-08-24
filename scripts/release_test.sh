./scripts/bumps_up.sh
./scripts/build.sh

twine upload --repository testpypi dist/*
