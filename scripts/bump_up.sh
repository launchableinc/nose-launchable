current=`cat nose_launchable/version.py`

read -p "Next version (current version: $current): " next
echo "__version__ = '$next'" > nose_launchable/version.py

git checkout -b bumps_up_to_$next
git commit -am "Bumps up to $next"