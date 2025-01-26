#!/bin/bash
cd /home/site/wwwroot
export PYTHONPATH=/home/site/wwwroot
gunicorn --config gunicorn.conf.py app:app