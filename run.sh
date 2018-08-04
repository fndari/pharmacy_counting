#!/bin/bash

export PYTHONPATH="src/":$PYTHONPATH
# python3.6 src/pharmacy_counting/run.py
python3 -m pharmacy_counting.run
