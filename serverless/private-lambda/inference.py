
import os


def handler(event, context):
    lib_dir = os.environ["LIB_DIR"]
    files = os.listdir(lib_dir)
    print("Found these files", files)
