"""Tests that Lambda URL handler works as expected.

To execute these tests succesfully, you need the models available locally.
You can obtain them by using the original model source code () or by using the correct
hugging face ID to download them. 

You can also request access to S3 Bucket where I have them stored.

- Paolo Rechia 17.09.2022

"""
import os
from unittest.mock import patch
import json


@patch.dict(os.environ, {"MNT_DIR": "/mnt/fs"})
def test_handler():
    from example_lambda_url_handler import handler
    response = handler(
        {
            "body": json.dumps(
                {"prompt": "A wild forest", "num_inference_steps": "1"}
            ),
        },
        None
    )
    body = json.loads(response["body"])
    assert body["image"]
    bytes_img = body["image"].encode("latin1")
    with open("test_result.png", "w+b") as fp:
        fp.write(bytes_img)
