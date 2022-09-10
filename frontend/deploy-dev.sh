#!/bin/bash

cd web-app
npm run build:development
cd -
sls deploy -s dev
