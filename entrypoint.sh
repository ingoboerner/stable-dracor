#!/bin/bash
/usr/local/bin/dockerd-entrypoint.sh &
jupyter lab --ip=* --allow-root --port=8888 --no-browser --notebook-dir=/home/dracor/notebooks --NotebookApp.token=''
