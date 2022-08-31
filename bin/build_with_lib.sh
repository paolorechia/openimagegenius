#!/bin/bash

# Garbage script to build local library and save it along with the project usual dependencies.
# Not pretty, but useful

lib_name="openimage_backend_lib"
origin_folder="$(pwd)"
output_folder="$(pwd)/manual_dist"
lib_output_folder="../lib_build"
lib_output_folder_to_copy="../../lib_build"

if [[ "$1" == "build" ]]; then
    echo "Building..."
    lib_folder="../../openimage_backend_lib"

    echo "Changing to $lib_folder"
    cd $lib_folder
    python3 -m build --outdir $lib_output_folder

    echo "Returning to origin folder $origin_folder"
    cd $origin_folder
fi

echo "Trimming requirements.txt"
sed -i.bak "/${lib_name}/d" requirements.txt
echo "Downloading requirements.txt"
echo "Saving to $output_folder"

pip download -r requirements.txt --dest $output_folder --verbose
echo "Adding lib name back to requirements.txt"

echo $lib_name >> requirements.txt
echo $(pwd)
cp -r ${lib_output_folder_to_copy}/* $output_folder