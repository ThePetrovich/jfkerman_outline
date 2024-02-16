#!/bin/bash

echo Activating venv
source ./venv/bin/activate

echo Starting scheduler
python ./manage.py schedule
