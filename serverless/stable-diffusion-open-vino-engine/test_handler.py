"""Tests that Lambda URL handler works as expected.

To execute these tests succesfully, you need the models available locally.
You can obtain them by using the original model source code () or by using the correct
hugging face ID to download them. 

You can also request access to S3 Bucket where I have them stored.

- Paolo Rechia 17.09.2022

"""
import json
import os
import sys
import logging
from unittest.mock import MagicMock, patch

s3_mock = MagicMock()
boto3_mock = MagicMock()
boto3_mock.client.return_value = s3_mock

@patch.dict(os.environ, {"MNT_DIR": "/mnt/fs", "S3_BUCKET": "test-bucket"})
@patch("boto3.client", return_value=boto3_mock)
def test_handler(boto3_mock):
    from handler import handler
    body = json.dumps(
        {
            "message_type": "request_prompt",
            "prompt": "A wild forest",
            "request_id": "123",
            "s3_url": "s3_url",
            "s3_fields": {}
        }
    )
    sqs_records = {
        "Records": [
            {
                "messageId": "19dd0b57-b21e-4ac1-bd88-01bbb068cb78",
                "receiptHandle": "MessageReceiptHandle",
                "body": body,
                "attributes": {
                    "ApproximateReceiveCount": "1",
                    "SentTimestamp": "1523232000000",
                    "SenderId": "123456789012",
                    "ApproximateFirstReceiveTimestamp": "1523232000001"
                },
                "messageAttributes": {},
                "md5OfBody": "7b270e59b47ff90a553787216d55d91d",
                "eventSource": "aws:sqs",
                "eventSourceARN": "arn:aws:sqs:us-east-1:123456789012:MyQueue",
                "awsRegion": "us-east-1"
            }
        ]
    }
    response = handler(sqs_records, None)
    print(response)
    assert response["statusCode"] == 200
    boto3_mock.assert_called_with("s3")
