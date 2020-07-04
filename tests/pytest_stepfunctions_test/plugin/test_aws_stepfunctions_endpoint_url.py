import json
from string import Template
from typing import Any, Dict, List

import boto3
import pytest
from botocore.stub import Stubber

from pytest_stepfunctions_test.utility import StepFunctionsRunner


def test_simple_state_machine(aws_stepfunctions_endpoint_url: str) -> None:
    definition: str = """
    {
      "StartAt": "Hello",
      "States": {
        "Hello": {
          "Type": "Pass",
          "Result": {
            "text": "abc"
          },
          "ResultPath": "$.append",
          "End": true
        }
      }
    }
    """

    response = StepFunctionsRunner(aws_stepfunctions_endpoint_url).run(definition=definition, input_string='{"n":123}')

    assert "SUCCEEDED" == response["status"]
    assert {"append": {"text": "abc"}, "n": 123} == json.loads(response["output"])


@pytest.fixture
def mock_emr_client_stubber(mocker: Any) -> Stubber:
    real_emr_client = boto3.client("emr")
    stubber: Stubber = Stubber(real_emr_client)
    mocker.patch(__name__ + ".boto3").client.return_value = real_emr_client

    return stubber


def list_emr_cluster_ids(event: Dict[str, Any], *_args: Any, **_kwargs: Any) -> List[str]:
    emr_client = boto3.client("emr")
    response = emr_client.list_clusters(ClusterStates=event["states"])

    if "Clusters" not in response:
        return []

    return [item["Id"] for item in response["Clusters"]]


def test_boto3_involved_state_machine(aws_stepfunctions_endpoint_url: str, mock_emr_client_stubber: Stubber) -> None:
    lambda_arn_base: str = "arn:aws:lambda:us-east-1:123456789012:function:"
    list_emr_cluster_ids_lambda_arn: str = (
        lambda_arn_base + list_emr_cluster_ids.__module__ + "." + list_emr_cluster_ids.__name__
    )

    definition: str = Template(
        """
        {
          "StartAt": "ListEMRClusterIds",
          "States": {
            "ListEMRClusterIds": {
              "Type": "Task",
              "Resource": "${ListEMRClusterIdsLambdaArn}",
              "ResultPath": "$.emr_cluster_ids",
              "End": true
            }
          }
        }
        """,
    ).safe_substitute(ListEMRClusterIdsLambdaArn=list_emr_cluster_ids_lambda_arn)
    input_string = '{"states": ["RUNNING", "WAITING"]}'

    service_response = {"Clusters": [{"Id": "j-0000000"}, {"Id": "j-0000001"}, {"Id": "j-0000002"}]}
    expected_params = {"ClusterStates": ["RUNNING", "WAITING"]}
    mock_emr_client_stubber.add_response(
        "list_clusters", service_response=service_response, expected_params=expected_params
    )

    with mock_emr_client_stubber:
        response = StepFunctionsRunner(aws_stepfunctions_endpoint_url).run(
            definition=definition, input_string=input_string
        )

    assert "SUCCEEDED" == response["status"]
    assert ["j-0000000", "j-0000001", "j-0000002"] == json.loads(response["output"])["emr_cluster_ids"]
    mock_emr_client_stubber.assert_no_pending_responses()
