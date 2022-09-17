import requests
import json

headers = {"content-type": "application/json"}
url = "http://localhost:9000/2015-03-31/functions/function/invocations"

body = json.dumps({"prompt": "beautiful tree", "num_inference_steps": 1})
response = requests.post(url, json={"body": body}, headers=headers)
print(response)
response.raise_for_status()
j = response.json()
body = json.loads(j["body"])
print(body["message"])
bytes_img = body["image"].encode("latin1")
with open("test_result.png", "w+b") as fp:
    fp.write(bytes_img)
