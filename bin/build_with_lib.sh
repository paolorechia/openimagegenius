#!/bin/bash

lib_name="openimage_backend_lib"
origin_folder="$(pwd)"
output_folder="$(pwd)/manual_dist"
echo "Saving to $output_folder"

lib_folder="../../openimage_backend_lib"

echo "Changing to $lib_folder"
cd $lib_folder
python3 -m build --outdir $output_folder

echo "Returning to origin folder $origin_folder"
cd $origin_folder

echo "Trimming requirements.txt"
sed -i.bak "/${lib_name}/d" requirements.txt
echo "Downloading requirements.txt"
pip download -r requirements.txt --dest $output_folder
echo "Adding lib name back to requirements.txt"

echo $lib_name >> requirements.txt