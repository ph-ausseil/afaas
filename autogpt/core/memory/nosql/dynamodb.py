from __future__ import annotations

from logging import Logger
from typing import TYPE_CHECKING, List

import boto3
from botocore.exceptions import NoCredentialsError

if TYPE_CHECKING:
    from autogpt.core.memory.base import Memory


class DynamoDBMemory(Memory):
    """
    DO NOT USE : TEMPLATE UNDER DEVELOPMENT, WOULD HAPPILY TAKE HELP :-)

    Args:
        Memory (_type_): _description_
    """

    def __init__(self, logger: Logger):
        self._dynamodb = None
        self._logger = logger

    def connect(self, **kwargs):
        region_name = kwargs.get("region_name")
        self._dynamodb = boto3.resource("dynamodb", region_name=region_name)

        # Test connection by trying to list tables
        try:
            dynamodb_client = boto3.client("dynamodb", region_name=region_name)
            dynamodb_client.list_tables()
        except NoCredentialsError:
            self._logger.error("No AWS credentials found.")
            raise
        except Exception as e:
            self._logger.error(f"Unable to connect to DynamoDB: {e}")
            raise e
        else:
            self._logger.info("Successfully connected to DynamoDB.")

    def get(self, key: dict, table_name: str):
        table = self._dynamodb.Table(table_name)
        response = table.get_item(Key=key)
        return response["Item"]

    def add(self, key: dict, value: dict, table_name: str):
        table = self._dynamodb.Table(table_name)
        item = {**key, **value}
        table.put_item(Item=item)

    def update(self, key: dict, value: dict, table_name: str):
        table = self._dynamodb.Table(table_name)
        # Building update expression
        update_expression = "SET " + ", ".join(f"{k}=:{k}" for k in value)
        expression_attribute_values = {f":{k}": v for k, v in value.items()}

        table.update_item(
            Key=key,
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values,
        )

    def delete(self, key: dict, table_name: str):
        table = self._dynamodb.Table(table_name)
        table.delete_item(Key=key)

    def list(self, table_name: str) -> List[dict]:
        table = self._dynamodb.Table(table_name)
        response = table.scan()
        return response["Items"]
