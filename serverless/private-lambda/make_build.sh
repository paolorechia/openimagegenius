#!/bin/bash

mkdir build
mkdir packages
pip install -r requirements.txt --target packages
cd packages
zip build.zip *
cd -