import importlib
import json
import re
import sys
import traceback
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler
from typing import Match, Optional
from urllib.parse import ParseResult, urlparse


@dataclass
class LambdaContext:
    function_name: str = "test-function"
    memory_limit_in_mb: int = 128
    invoked_function_arn: str = (
        f"arn:aws:lambda:us-east-1:123456789012:function{function_name}"
    )
    aws_request_id: str = "da658bd3-2d6f-4e7b-8ec2-937234644fdc"


class AWSLambdaRequestHandler(BaseHTTPRequestHandler):
    def do_POST(self) -> None:
        try:
            parsed_path: ParseResult = urlparse(self.path)

            match: Optional[Match[str]] = re.match(
                "/2015-03-31/functions/(?P<function_name>[a-zA-Z0-9_.]+)/invocations",
                parsed_path.path,
            )
            if match:
                return self._handle_invoke(function_name=match.group("function_name"))

            raise Exception(f"Unrecognized path: {self.path}")

        except Exception:
            e_type, e_value, e_traceback = sys.exc_info()
            output = {
                "errorMessage": str(e_value),
                "errorType": e_type.__name__ if e_type else "",
                "stackTrace": traceback.format_tb(e_traceback),
            }
            self.wfile.write(
                b"HTTP/1.1 200 OK\nX-Amz-Function-Error: Unhandled\n\n"
                + json.dumps(output, separators=(",", ":")).encode()
            )

    def _retrieve_payload(self) -> bytes:
        if "Content-Length" in self.headers:
            content_length: int = int(self.headers["Content-Length"])
            return self.rfile.read(content_length) if content_length > 0 else b"{}"
        assert self.headers["Transfer-Encoding"] == "chunked"

        content: bytes = b""
        while True:
            size: int = int(self.rfile.readline().rstrip(), 16)
            if size == 0:
                break
            content += self.rfile.readline()[:-2]
        return content

    def _handle_invoke(self, function_name: str) -> None:
        module_name, method_name = function_name.rsplit(".", maxsplit=1)

        context = LambdaContext(function_name)

        event = json.loads(self._retrieve_payload().decode())
        module = importlib.import_module(module_name)
        output = getattr(module, method_name)(event, context)

        self.wfile.write(b"HTTP/1.1 200 OK\n\n" + json.dumps(output).encode())
