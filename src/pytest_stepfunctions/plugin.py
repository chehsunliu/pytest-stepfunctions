import threading
from http.server import HTTPServer
from typing import Iterator, Any

import pytest

from pytest_stepfunctions.services.aws_lambda import AWSLambdaRequestHandler

_DEFAULT_STEPFUNCTIONS_ENDPOINT_URL: str = "http://0.0.0.0:8083"
_DEFAULT_LAMBDA_ADDRESS: str = "0.0.0.0"
_DEFAULT_LAMBDA_PORT: int = 13000


def pytest_addoption(parser: Any) -> None:
    group = parser.getgroup("pytest-stepfunctions")
    group.addoption(
        "--pytest-stepfunctions-endpoint-url",
        action="store",
        dest="pytest_stepfunctions_endpoint_url",
        default=_DEFAULT_STEPFUNCTIONS_ENDPOINT_URL,
        help=f"The address of the StepFunctions service (default: {_DEFAULT_STEPFUNCTIONS_ENDPOINT_URL})",
    )
    group.addoption(
        "--pytest-stepfunctions-lambda-address",
        action="store",
        dest="pytest_stepfunctions_lambda_address",
        default=_DEFAULT_LAMBDA_ADDRESS,
        help=f"The address of the internal simulate Lambda service (default: {_DEFAULT_LAMBDA_ADDRESS})",
    )
    group.addoption(
        "--pytest-stepfunctions-lambda-port",
        action="store",
        dest="pytest_stepfunctions_lambda_port",
        type=int,
        default=_DEFAULT_LAMBDA_PORT,
        help=f"The port of the internal simulate Lambda service (default: {_DEFAULT_LAMBDA_PORT}",
    )


def start_http_server(http_server: HTTPServer) -> None:
    http_server.serve_forever()


@pytest.fixture(scope="session")
def aws_lambda_endpoint_url(request: Any) -> Iterator[str]:
    lambda_address: str = request.config.getoption("pytest_stepfunctions_lambda_address")
    lambda_port: int = request.config.getoption("pytest_stepfunctions_lambda_port")

    http_server = HTTPServer((lambda_address, lambda_port), AWSLambdaRequestHandler)
    t = threading.Thread(target=start_http_server, args=(http_server,))
    t.start()

    yield f"http://{lambda_address}:{lambda_port}"

    http_server.shutdown()
    t.join()


@pytest.fixture(scope="session")
def aws_stepfunctions_endpoint_url(request: Any, aws_lambda_endpoint_url: str) -> Iterator[str]:
    assert aws_lambda_endpoint_url is not None

    stepfunctions_endpoint_url: str = request.config.getoption("pytest_stepfunctions_endpoint_url")
    yield stepfunctions_endpoint_url
