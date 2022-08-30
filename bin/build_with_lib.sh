#!/bin/bash

lib_name="openimage_backend_lib"
origin_folder="$(pwd)"
output_folder="$(pwd)/manual_dist"
# echo "Saving to $output_folder"

# lib_folder="/Users/paolorechia/dev/openimagegenius/openimage_backend_lib"

# echo "Changing to $lib_folder"
# cd $lib_folder
# python3 -m build --outdir $output_folder

# echo "Returning to origin folder $origin_folder"
# cd $origin_folder
pip download -r requirements.txt --dest $output_folder