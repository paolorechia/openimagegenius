import json
from handler import handler


def test_handler():
    response = handler(
        {
            "body": json.dumps(
                {"prompt": "A wild forest", "num_inference_steps": "1"}
            ),
        },
        None,
        "./models" # Hack models_dir into handler for local exec
    )
    # print(response)
    body = json.loads(response["body"])
    assert body["image"]
    bytes_img = body["image"].encode("latin1")
    with open("test_result.png", "w+b") as fp:
        fp.write(bytes_img)
