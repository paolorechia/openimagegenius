#!/bin/bash

cd web-app
npm run build:production
cd -
sls deploy -s prod
