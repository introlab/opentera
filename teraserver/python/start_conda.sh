#!/bin/bash
SCRIPT=$(readlink -f $0)
SCRIPTPATH=`dirname $SCRIPT`
echo "$SCRIPTPATH"
$SCRIPTPATH/env/python-3.6/bin/python3 $SCRIPTPATH/TeraServer.py
