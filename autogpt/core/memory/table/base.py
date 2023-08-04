from __future__ import annotations

import abc
import uuid
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    List,
    Literal,
    Optional,
    TypedDict,
    Union,
)

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from autogpt.core.memory.base import NewMemory

ComparisonOperator = Callable[[Any, Any], bool]
FilterItem = TypedDict(
    "FilterItem", {"value": Any, "operator": Union[str, ComparisonOperator]}
)
FilterDict = Dict[str, FilterItem]

# class KeyEnum(Enum):
#     primary_key: str
#     secondary_key: str
#     third_key: str

# class KeyMeta(type):
#     def __init__(cls, name: str, bases: tuple[Type], attrs: dict[str, Any]):
#         key_attrs = {}
#         if "primary_key" in attrs:
#             key_attrs["primary_key"] = attrs["primary_key"]
#         if "secondary_key" in attrs:
#             key_attrs["secondary_key"] = attrs["secondary_key"]
#         if "third_key" in attrs:
#             key_attrs["third_key"] = attrs["third_key"]

#         if key_attrs:
#             cls.Key = KeyEnum("Key", key_attrs)


# TODO : Adopt Configurable ?
class BaseTable(abc.ABC, BaseModel):
    table_name: str = Field(default_factory=lambda: "")
    memory: NewMemory

    def __init__(self, memory=NewMemory):
        self.memory = memory

    # def add(self, value: dict) -> uuid:
    #     id = uuid.uuid4()
    #     value["id"] = id
    #     self.memory.add(key=id, value=value, table_name=self.table_name)
    #     return id

    @abc.abstractmethod
    def add(self, value: dict) -> uuid:
        id = uuid.uuid4()
        key = {"primary_key": value.get(self.primary_key, id)}
        if hasattr(self, "secondary_key") and self.secondary_key in value:
            key["secondary_key"] = value[self.secondary_key]
        self.memory.add(key=key, value=value, table_name=self.table_name)
        return id

    @abc.abstractmethod
    def get(self, id: uuid) -> Any:
        key = {"primary_key": id}
        if hasattr(self, "secondary_key") and self.secondary_key:
            key["secondary_key"] = self.secondary_key
        return self.memory.get(key=key, table_name=self.table_name)

    @abc.abstractmethod
    def update(self, id: uuid, value: dict):
        key = {"primary_key": id}
        if hasattr(self, "secondary_key") and self.secondary_key in value:
            key["secondary_key"] = value[self.secondary_key]
        self.memory.update(key=key, value=value, table_name=self.table_name)

    @abc.abstractmethod
    def delete(self, id: uuid):
        key = {"primary_key": id}
        if hasattr(self, "secondary_key") and self.secondary_key:
            key["secondary_key"] = self.secondary_key
        self.memory.delete(key=key, table_name=self.table_name)

    def list(
        self,
        filter: FilterDict = {},
        order_column: Optional[str] = None,
        order_direction: Literal["asc", "desc"] = "desc",
    ) -> List[Dict[str, Any]]:
        """
        Retrieve a filtered and optionally ordered list of items from the table.

        Parameters:
            filter (FilterDict, optional): A dictionary containing the filter conditions.
                The keys in the filter dictionary represent the column names, and the values
                are dictionaries containing the 'value' and 'operator' keys.
                'value': The value used for comparison in the filter.
                'operator': The operator to use for comparison. It can be a custom callable or
                            one of the basic operators: ('>', '<', '==', '>=', 'in', 'not in',
                            '<=', '!=').
                            - For basic operators, use the operator symbol as a string, e.g., '>'.
                            - For custom operators, provide a callable that takes two arguments
                              and returns a bool indicating the result of the comparison.

            order_column (str, optional): The column name to use for sorting the results.
                Default: None.

            order_direction (str, optional): The order direction for sorting the results.
                Can be 'asc' (ascending) or 'desc' (descending). Default: 'asc'.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries containing the filtered items that
                                  match the specified conditions.

        Example:
            Suppose we have a BaseTable instance with the following data in the memory:

            data_list = [
                {'name': 'John', 'age': 25, 'city': 'New York'},
                {'name': 'Alice', 'age': 30, 'city': 'Los Angeles'},
                {'name': 'Bob', 'age': 22, 'city': 'Chicago'},
                {'name': 'Eve', 'age': 35, 'city': 'San Francisco'}
            ]

            # Example 1: Using basic operator '>' for age greater than 25
            filter_dict = {'age': {'value': 25, 'operator': '>'}}
            result = base_table.list(filter_dict)
            # Output: [{'name': 'Alice', 'age': 30, 'city': 'Los Angeles'},
            #          {'name': 'Eve', 'age': 35, 'city': 'San Francisco'}]

            # Example 2: Using custom operator for a specific filter
            def custom_comparison(value, filter_value):
                return len(value['city']) > len(filter_value)

            filter_dict = {'city': {'value': 'Chicago', 'operator': custom_comparison}}
            result = base_table.list(filter_dict)
            # Output: [{'name': 'John', 'age': 25, 'city': 'New York'},
            #          {'name': 'Alice', 'age': 30, 'city': 'Los Angeles'}]

            # Example 3: Using multiple filters with basic and custom operators
            filter_dict = {
                'age': {'value': 30, 'operator': '>='},
                'city': {'value': 'New York', 'operator': '!='},
                'name': {'value': 'Bob', 'operator': custom_comparison}
            }
            result = base_table.list(filter_dict)
            # Output: [{'name': 'Alice', 'age': 30, 'city': 'Los Angeles'}]
        """
        data_list = self.memory.list(table_name=self.table_name)
        filtered_data_list: List = []

        def greater_than(value: Any, filter_value: Any) -> bool:
            return value > filter_value

        def less_than(value: Any, filter_value: Any) -> bool:
            return value < filter_value

        def equal_to(value: Any, filter_value: Any) -> bool:
            return value == filter_value

        def greater_than_or_equal(value: Any, filter_value: Any) -> bool:
            return value >= filter_value

        def in_list(value: Any, filter_value: List[Any]) -> bool:
            return value in filter_value

        def not_in_list(value: Any, filter_value: List[Any]) -> bool:
            return value not in filter_value

        def less_than_or_equal(value: Any, filter_value: Any) -> bool:
            return value <= filter_value

        def not_equal_to(value: Any, filter_value: Any) -> bool:
            return value != filter_value

        operators: Dict[str, ComparisonOperator] = {
            ">": greater_than,
            "<": less_than,
            "==": equal_to,
            ">=": greater_than_or_equal,
            "in": in_list,
            "not in": not_in_list,
            "<=": less_than_or_equal,
            "!=": not_equal_to,
        }

        for data in data_list:
            filtered_data: Dict = {}
            for key, filter_data in filter.items():
                value = data.get(key)
                if value is not None:
                    filter_value = filter_data["value"]
                    comparison_operator = filter_data["operator"]
                    if callable(comparison_operator):
                        if comparison_operator(value, filter_value):
                            filtered_data[key] = value
                    elif comparison_operator in operators:
                        if operators[comparison_operator](value, filter_value):
                            filtered_data[key] = value
            if filtered_data:
                filtered_data_list.append(filtered_data)

        if order_column:
            filtered_data_list.sort(
                key=lambda x: x[order_column], reverse=order_direction == "desc"
            )

        return filtered_data_list


class AgentsTable(BaseTable):
    table_name = "agents"
    primary_key = "agent_id"
    secondary_key = "user_id"
    third_key = "agent_type"

    # This is add agent the method to create an agent, I need help to define how should be declared this method
    # def add(self, value  : dict) ?
    # def add(self, user_id, value  : dict) ?
    # def add(self, user_id, agent_type, value  : dict) ?
    # def add_agent(self, user_id: uuid, agent_type: str, value: dict) -> uuid:
    #     agent_id = uuid.uuid4() # generate a new id for the agent
    #     value.update({"agent_id": agent_id, "user_id": user_id, "agent_type": agent_type}) # add additional fields
    #     self.memory.add(key=agent_id, value=value, table_name=self.table_name) # add the new agent to the database
    #     return agent_id

    # def add(self,user_id , value  : dict) :
    #     id = uuid.uuid4()
    #     value["id"] = id
    #     self.memory.add(key=id, value=value, table_name=self.table_name)
    #     return id

    # def add(self,user_id , value  : dict) :
    #     id = uuid.uuid4()
    #     value["id"] = id
    #     self.memory.add(key=id, value=value, table_name=self.table_name)
    #     return id

    # NOTE : overwrite parent update
    # Perform any custom logic needed for updating an agent
    def update(self, id: uuid, value: dict):
        super().update(id=id, value=value)

    # def add(self, value: dict) -> uuid:

    # def get(self, id: uuid) -> Any:

    # def get_from_date(self, id: uuid) -> Any:

    # def get_from_date(self, id: uuid) -> Any:

    # def delete(self, id: uuid):

    # def list(self) ->dict:

    # def list(self,
    # agent_type = None,
    # from_date = None ,
    # order_column = None,
    # order_direction = 'asc') ->dict:


class MessagesTable(BaseTable):
    table_name = "messages_history"
    primary_key = "message_id"
    secondary_key = "agent_id"


class UsersInformationsTable(BaseTable):
    table_name = "users_informations"
    primary_key = "user_id"


# class UsersAgentsTable(BaseTable):
#     table_name = "users_agents"
