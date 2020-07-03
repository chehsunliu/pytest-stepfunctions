import http.client
import json
from io import BytesIO
from typing import NamedTuple, Any, Dict, Optional
from urllib.parse import urlparse, ParseResult

import boto3
import pytest


class MyCase(NamedTuple):
    description: str
    function_name: str
    payload: Dict[str, Any]
    expected_payload: Optional[Dict[str, Any]]


def add(event: Dict[str, Any], *_args: Any, **_kwargs: Any) -> Dict[str, int]:
    assert isinstance(event["a"], int)
    assert isinstance(event["b"], int)
    return {"answer": event["a"] + event["b"]}


def empty(event: Dict[str, Any], *_args: Any, **_kwargs: Any) -> None:
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
def lambda_client(aws_lambda_endpoint_url: str) -> boto3.client:
    return boto3.client(
        "lambda",
        region_name="us-east-1",
        aws_access_key_id="AKIAIOSFODNN7EXAMPLE",
        aws_secret_access_key="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
        endpoint_url=aws_lambda_endpoint_url,
    )


@pytest.mark.parametrize("my_case", my_cases, ids=[my_case.description for my_case in my_cases])
def test_invoke_success_by_lambda_client(lambda_client: boto3.client, my_case: MyCase) -> None:
    response = lambda_client.invoke(FunctionName=my_case.function_name, Payload=json.dumps(my_case.payload).encode())

    assert 200 == response["StatusCode"]
    assert my_case.expected_payload == json.load(response["Payload"])


@pytest.mark.parametrize("my_case", my_cases, ids=[my_case.description for my_case in my_cases])
def test_invoke_success_by_stepfunctions(aws_lambda_endpoint_url: str, my_case: MyCase) -> None:
    """
    AWS StepFunctions Local uses `Transfer-Encoding: chunked` instead of a fixed `Content-Length`
    to transfer the payload.
    """

    parsed_result: ParseResult = urlparse(aws_lambda_endpoint_url)
    assert parsed_result.hostname is not None

    conn = http.client.HTTPConnection(parsed_result.hostname, port=parsed_result.port)
    conn.connect()
    conn.putrequest("POST", f"/2015-03-31/functions/{my_case.function_name}/invocations")
    conn.putheader("Content-Type", "application/json")
    conn.putheader("Transfer-Encoding", "chunked")
    conn.endheaders()

    payload = BytesIO(json.dumps(my_case.payload).encode())
    buffer = bytearray(5)
    while True:
        length: int = payload.readinto(buffer)
        conn.send(b"%x\r\n" % length)

        if length > 0:
            conn.send(bytes(buffer[:length]) + b"\r\n")
        else:
            break

    response: http.client.HTTPResponse = conn.getresponse()
    assert 200 == response.status
    assert my_case.expected_payload == json.load(response)

    conn.close()


def fail(event: Dict[str, Any], *_args: Any, **_kwargs: Any) -> None:
    assert event is not None
    raise Exception("qq qq qq")


def test_invoke_failure_by_lambda_client(lambda_client: boto3.client) -> None:
    function_name: str = fail.__module__ + "." + fail.__name__
    response = lambda_client.invoke(FunctionName=function_name, Payload=json.dumps({}).encode())
    payload = json.load(response["Payload"])

    assert 200 == response["StatusCode"]
    assert "qq qq qq" == payload["errorMessage"]
    assert "Exception" == payload["errorType"]


def test_unsupported_function(lambda_client: boto3.client) -> None:
    response = lambda_client.create_alias(FunctionName="a", Name="current", FunctionVersion="10")
    assert 200 == response["ResponseMetadata"]["HTTPStatusCode"]
