#!/bin/bash

echo Activating venv
source ./venv/bin/activate

echo Starting server
daphne config.asgi:application -p 5050
