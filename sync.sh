#!/usr/bin/env bash

# This script is used to sync the library folder between local and remote
# Requires rclone to be installed

REMOTE=files:/000.FILES/003.PROJECTS/LIBRARY_DATA_VIZ/
LOCAL=~/Projects/LIBRARY_DATA_VIZ/

# Sync function
function sync() {
    rclone sync $1 $2 --progress -v --transfers 10 --checkers 5 --exclude-from .rclone_ignore
}

# Check if arguments are provided
if [ -z "$1" ] || [ -z "$2" ]; then
    echo "Usage: sync.sh <source> <destination>"
    exit 1
fi

# Check if rclone is installed
if ! command -v rclone &>/dev/null; then
    echo "rclone could not be found"
    exit 1
fi

# Sync based on arguments
if [ "$1" == "local" ] && [ "$2" == "remote" ]; then
    echo "Syncing from local to remote"
    sync $LOCAL $REMOTE
elif [ "$1" == "remote" ] && [ "$2" == "local" ]; then
    echo "Syncing from remote to local"
    sync $REMOTE $LOCAL
else
    echo "Invalid arguments"
    exit 1
fi
