from typing import List
from copy import deepcopy

base_policy_obj = {
    "principalId": "user",
    "policyDocument": {
        "Version": "2012-10-17",
        "Statement": []
    },
    "context": {},
}

def create_policy(resource, effect="Deny"):
    policy_obj = deepcopy(base_policy_obj)
    policy_obj["policyDocument"]["Statement"].append(
        {
            "Action": "execute-api:Invoke",
            "Effect": effect,
            "Resource": resource
        }
    )
    return policy_obj


def find_resources(event, stage) -> List[str]:
    requested_resource = event.get("methodArn")
    resource_wildcard = requested_resource.split(f"/{stage}")[0] + "/*"
    return resource_wildcard