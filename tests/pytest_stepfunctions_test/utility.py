import time
from typing import Any, Dict
from uuid import uuid4

import boto3


class StepFunctionsRunner:
    def __init__(self, endpoint_url: str):
        self.endpoint_url: str = endpoint_url

    def run(self, definition: str, input_string: str) -> Dict[str, Any]:
        sfn_client = boto3.client("stepfunctions", endpoint_url=self.endpoint_url)

        state_machine_arn = sfn_client.create_state_machine(
            name=str(uuid4()), definition=definition, roleArn="arn:aws:iam::012345678901:role/DummyRole",
        )["stateMachineArn"]
        execution_arn: str = sfn_client.start_execution(
            stateMachineArn=state_machine_arn, name=str(uuid4()), input=input_string
        )["executionArn"]

        while True:
            response = sfn_client.describe_execution(executionArn=execution_arn)
            if response["status"] != "RUNNING":
                return response
            time.sleep(0.5)
