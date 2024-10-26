from __future__ import annotations

from typing import TYPE_CHECKING

import boto3
from botocore.exceptions import NoCredentialsError

if TYPE_CHECKING:
    from AFAAS.interfaces.db.db import AbstractMemory

from AFAAS.interfaces.db.db_nosql import NoSQLMemory


class DynamoDBMemory(NoSQLMemory):
    """
    DO NOT USE : TEMPLATE UNDER DEVELOPMENT, WOULD HAPPILY TAKE HELP :-)

    Args:
        Memory (_type_): _description_
    """

    def __init__(
        self,
        settings: AbstractMemory.SystemSettings,
    ):
        super().__init__(settings)
        self._dynamodb = None

    async def connect(
        self,
        dynamodb_region_name=None,
        aws_access_key_id=None,
        aws_secret_access_key=None,
    ):
        # Connecting to DynamoDB with specified region and credentials
        dynamodb_region_name = dynamodb_region_name | self.dynamodb_region_name
        aws_access_key_id = aws_access_key_id | self.aws_access_key_id
        aws_secret_access_key = aws_secret_access_key | self.aws_secret_access_key
        dynamodb_resource = boto3.resource(
            "dynamodb",
            region_name=dynamodb_region_name,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )
        return dynamodb_resource
        try:
            # Test connection by trying to list tables
            dynamodb_client = boto3.client(
                "dynamodb",
                region_name=dynamodb_region_name,
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
            )
            dynamodb_client.list_tables()
        except NoCredentialsError:
            LOG.error("No AWS credentials found.")
            raise
        except Exception as e:
            LOG.error(f"Unable to connect to DynamoDB: {e}")
            raise e
        else:
            LOG.info("Successfully connected to DynamoDB.")

    async def get(self, key: dict, table_name: str):
        table = self._dynamodb.Table(table_name)
        response = table.get_item(Key=key)
        return response["Item"]

    async def add(self, key: dict, value: dict, table_name: str):
        table = self._dynamodb.Table(table_name)
        item = {**key, **value}
        table.put_item(Item=item)

    async def update(self, key: dict, value: dict, table_name: str):
        table = self._dynamodb.Table(table_name)
        # Building update expression
        update_expression = "SET " + ", ".join(f"{k}=:{k}" for k in value)
        expression_attribute_values = {f":{k}": v for k, v in value.items()}

        table.update_item(
            Key=key,
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values,
        )

    async def delete(self, key: dict, table_name: str):
        table = self._dynamodb.Table(table_name)
        table.delete_item(Key=key)

    async def list(self, table_name: str) -> list[dict]:
        table = self._dynamodb.Table(table_name)
        response = table.scan()
        return response["Items"]
