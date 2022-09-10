from io import BytesIO
from zipfile import ZipFile
import boto3
import os

s3_client = boto3.client("s3")
model_files = [
    "text_encoder.bin",
    "text_encoder.xml",
    "unet.bin",
    "unet.xml",
    "vae_decoder.bin",
    "vae_decoder.xml",
    "vae_encoder.bin",
    "vae_encoder.xml"
]


def install_models(models_dir):
    try:
        os.makedirs(models_dir)
    except FileExistsError:
        pass

    for model in model_files:
        print(f"Fetching {model} from S3 Bucket")
        response = s3_client.get_object(
            Bucket=os.environ["INSTALLER_BUCKET_NAME"],
            Key=model
        )
        # Overflow on big files:
        # Fix from: https://stackoverflow.com/a/70909130/8628527
        buf = bytearray(response['ContentLength'])
        view = memoryview(buf)
        pos = 0
        while True:
            chunk = response['Body'].read(67108864)
            if len(chunk) == 0:
                break
        view[pos:pos+len(chunk)] = chunk
        filename = os.path.join(models_dir, model)
        print(f"Writing buffer to file {filename}")
        with open(filename, "wb") as fp:
            fp.write(buf)


def install_libraries(lib_dir):
    print("Creating lib directory...")
    try:
        os.makedirs(lib_dir)
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
    files = zip_file.namelist()
    print("Zip has the following files")
    print(files)
    for file_ in files:
        file_bytes = zip_file.read(file_)
        output_filename = os.path.join(lib_dir, file_)
        print(f"Writing file {file_} to {output_filename}")
        base_path = "/".join(output_filename.split("/")[0:-1])
        try:
            os.makedirs(base_path)
        except FileExistsError:
            pass
        try:
            with open(output_filename, "w+b") as fp:
                fp.write(file_bytes)
        except IsADirectoryError:
            pass

    lib_files = os.listdir(lib_dir)
    print("List of files in lib directory after extracting and writing zip archive to disk:", lib_files)


def handler(event, context):
    print("Trying to access EFS filesystem")
    mount_dir = os.environ['MNT_DIR']
    lib_dir = os.environ["LIB_DIR"]
    models_dir = os.environ["MODELS_DIR"]

    os.chdir(mount_dir)
    print("Changed to dir successfully...")
    print("Current dir", os.getcwd())
    files = os.listdir(mount_dir)
    print("List of files in directory", files)

    # install_libraries(lib_dir)
    install_models(models_dir)
