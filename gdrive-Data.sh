#!/bin/bash
#12 2 * * * /path/gdrive-Data.sh
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
userDir=$(echo "$DIR" | awk -F "/" '{print $3}')
path="/home/$userDir/"
grive -s meteor-Data -p $path
