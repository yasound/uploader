#!/bin/bash
# This script bootstraps a virtualenv 
# environement for demos

# Starts
if [ ! -f ./vtenv/bin/python ]
then
    if [ ! -f ./virtualenv.py ]
    then
        echo "Please get a copy of virtualenv.py"
        exit 1
    fi
    python virtualenv.py vtenv
fi
vtenv/bin/pip install -r requirements.txt --download-cache=eggs
echo " * Done"
exit

