#!/bin/bash

anvil --accounts 0 > /dev/null &
cd /app/python
python3 main.py