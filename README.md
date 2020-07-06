# pytest-stepfunctions

![GitHub Actions/CI](https://github.com/chehsunliu/pytest-stepfunctions/workflows/CI/badge.svg)
[![codecov](https://codecov.io/gh/chehsunliu/pytest-stepfunctions/branch/master/graph/badge.svg)](https://codecov.io/gh/chehsunliu/pytest-stepfunctions)
[![pypi-version](https://img.shields.io/pypi/v/pytest-stepfunctions)](https://pypi.python.org/pypi/pytest-stepfunctions)
[![pypi-pyversions](https://img.shields.io/pypi/pyversions/pytest-stepfunctions)](https://pypi.python.org/pypi/pytest-stepfunctions)

A pytest fixture that makes you able to mock Lambda code during AWS StepFunctions local testing.

## Overview

AWS provides local Step Functions as a JAR and a Docker image for the quick testing without deployment. They described how to perform such task in [this article](https://docs.aws.amazon.com/step-functions/latest/dg/sfn-local-lambda.html) as well. I got excited at the very beginning, but soon ended up frustrated for still being unable to mock Lambda functions' external dependencies. Then I thought: what if initiate a Python thread with a fake Lambda service and use this fake service to execute Lambda functions? Fortunately, It works. 

## Installing

Use pip to install:

```bash
$ pip install pytest-stepfunctions
```

## Getting Started

Suppose there is a state machine that simply collects all the EMR cluster unique identifiers. Here is the state machine definition:

```json
{
  "StartAt": "ListIds",
  "States": {
    "ListIds": {
      "Type": "Task",
      "Resource": "${ListIdsLambdaArn}",
      "ResultPath": "$.cluster_ids",
      "End": true
    }
  }
}
```

and the Lambda code `my/pkg/emr.py`:

```python
import boto3


def list_ids(*args, **kwargs):
    emr_client = boto3.client("emr")
    response = emr_client.list_clusters()

    return [item["Id"] for item in response["Clusters"]]
```

### Creating a State Machine

In the test file `tests/test_foo.py`, create a Step Functions client with endpoint URL pointed to our Step Functions service, and use this client to create a state machine resource by using the definition above

```python
from string import Template

import boto3


def test_bar(aws_stepfunctions_endpoint_url):
    definition_template = Template("""
    {
      "StartAt": "ListIds",
      "States": {
        "ListIds": {
          "Type": "Task",
          "Resource": "${ListIdsLambdaArn}",
          "ResultPath": "$.cluster_ids",
          "End": true
        }
      }
    }
    """)
    list_ids_lambda_arn = "arn:aws:lambda:us-east-1:123456789012:function:my.pkg.emr.list_ids"
    definition = definition_template.safe_substitute(ListIdsLambdaArn=list_ids_lambda_arn)

    sfn_client = boto3.client("stepfunctions", endpoint_url=aws_stepfunctions_endpoint_url)
    state_machine_arn = sfn_client.create_state_machine(
        name="list-ids", definition=definition, roleArn="arn:aws:iam::012345678901:role/DummyRole"
    )
```

Note the internal fake Lambda service in pytest-stepfunctions will parse Lambda ARNs to recognize what to call.
