from io import BytesIO
from zipfile import ZipFile
import boto3
import os

s3_client = boto3.client("s3")


def handler(event, context):
    print("Trying to access EFS filesystem")
    mount_dir = os.environ['MNT_DIR']
    lib_dir = os.environ["LIB_DIR"]
    os.chdir(mount_dir)
    print("Changed to dir successfully...")

    print("Current dir", os.getcwd())
    files = os.listdir(mount_dir)
    print("List of files in directory", files)

    print("Creating lib directory...")
    try:
        os.mkdir("./lib")
    except FileExistsError:
        pass

    lib_files = os.listdir(lib_dir)
    print("List of existing files in lib directory", lib_files)

    response = s3_client.get_object(
        Bucket=os.environ["INSTALLER_BUCKET_NAME"],
        Key="build.zip"
    )
    print(response)
    zip_raw_buffer = BytesIO(response["Body"].read())
    print("Read zip file successfully from S3 bucket.", zip_raw_buffer)

    print("Trying to unzip zip file")
    zip_file = ZipFile(zip_raw_buffer)
    print(zip_file)
    print("Zip has the following files")
    files = zip_file.namelist()
    print(files)
    for file_ in files:
        file_bytes = zip_file.read(file_)
        output_filename = os.path.join(lib_dir, file_)
        print(f"Writing file {file_} to {output_filename}")
        with open(output_filename, "wb") as fp:
            fp.write(file_bytes)

    lib_files = os.listdir(lib_dir)
    print("List of files in lib directory after extracting and writing zip archive to disk:", lib_files)
