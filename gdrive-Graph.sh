#!/bin/bash
#2,12,22,32,42,52 * * * * /path/gdrive-Graph.sh
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
userDir=$(echo "$DIR" | awk -F "/" '{print $3}')
path="/home/$userDir/"
grive -s meteor-Graph -p $path
