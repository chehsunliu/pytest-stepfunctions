import json
from typing import NamedTuple, Any, Dict, Optional

import boto3
import pytest


class MyCase(NamedTuple):
    description: str
    function_name: str
    payload: Dict[str, Any]
    expected_payload: Optional[Dict[str, Any]]


def add(event, **_kwargs):
    assert isinstance(event["a"], int)
    assert isinstance(event["b"], int)
    return {"answer": event["a"] + event["b"]}


def empty(event, *_args, **_kwargs) -> None:
    assert event is not None
    return


my_cases = [
    MyCase(
        description="add",
        function_name=add.__module__ + "." + add.__name__,
        payload={"a": 3, "b": 4},
        expected_payload={"answer": 7},
    ),
    MyCase(
        description="lambda returns null",
        function_name=empty.__module__ + "." + empty.__name__,
        payload={"a": 3, "b": 4},
        expected_payload=None,
    ),
]


@pytest.fixture
def lambda_client(aws_lambda_endpoint: str) -> boto3.client:
    return boto3.client(
        "lambda",
        region_name="us-east-1",
        aws_access_key_id="AKIAIOSFODNN7EXAMPLE",
        aws_secret_access_key="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
        endpoint_url=aws_lambda_endpoint,
    )


@pytest.mark.parametrize("my_case", my_cases, ids=[my_case.description for my_case in my_cases])
def test_invoke(lambda_client: boto3.client, my_case: MyCase) -> None:
    response = lambda_client.invoke(FunctionName=my_case.function_name, Payload=json.dumps(my_case.payload).encode())

    assert 200 == response["StatusCode"]
    assert my_case.expected_payload == json.load(response["Payload"])
