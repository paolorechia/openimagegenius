#!/bin/bash

mkdir build
mkdir packages
pip install -r requirements.txt --target packages
cd packages
zip -r build.zip *
cd -
mv packages/build.zip build/build.zip
