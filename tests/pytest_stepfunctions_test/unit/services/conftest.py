import threading
from http.server import HTTPServer
from typing import Iterator, Tuple

import pytest

from pytest_stepfunctions.services.aws_lambda import AWSLambdaRequestHandler
from pytest_stepfunctions_test.utils import get_free_port


def start_http_server(http_server: HTTPServer) -> None:
    http_server.serve_forever()


@pytest.fixture(scope="session")
def aws_lambda_endpoint() -> Iterator[Tuple[str, str, int]]:
    address: str = "0.0.0.0"
    port: int = get_free_port()

    http_server = HTTPServer((address, port), AWSLambdaRequestHandler)
    t = threading.Thread(target=start_http_server, args=(http_server,))
    t.start()

    yield f"http://{address}:{port}", address, port

    http_server.shutdown()
    t.join()
