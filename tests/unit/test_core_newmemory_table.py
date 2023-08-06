from autogpt.core.memory.table.base import (
    AgentsTable,
    BaseTable,
    MessagesTable,
    UsersInformationsTable,
)

# Create test data for BaseTable
data_list = [
    {"name": "John", "age": 25, "city": "New York"},
    {"name": "Alice", "age": 30, "city": "Los Angeles"},
    {"name": "Bob", "age": 22, "city": "Chicago"},
    {"name": "Eve", "age": 35, "city": "San Francisco"},
]


# Mock Memory class
class MockMemory:
    def __init__(self):
        self.data = data_list

    def list(self, table_name):
        return self.data

    def add(self, key, value, table_name):
        pass

    def get(self, key, table_name):
        pass

    def update(self, key, value, table_name):
        pass

    def delete(self, key, table_name):
        pass


# Helper function to create BaseTable instance with MockMemory
def create_base_table():
    memory = MockMemory()
    return BaseTable(memory=memory)


# Helper function to create AgentsTable instance with MockMemory
def create_agents_table():
    memory = MockMemory()
    return AgentsTable(memory=memory)


# Helper function to create MessagesTable instance with MockMemory
def create_messages_table():
    memory = MockMemory()
    return MessagesTable(memory=memory)


# Helper function to create UsersTable instance with MockMemory
def create_users_table():
    memory = MockMemory()
    return UsersInformationsTable(memory=memory)


# Test BaseTable.list method with different filter and order conditions
def test_base_table_list():
    base_table = create_base_table()

    # Test 1: Using basic operator '>' for age greater than 25
    filter_dict = {"age": {"value": 25, "operator": ">"}}
    result = base_table.list(filter_dict)
    assert result == [
        {"name": "Alice", "age": 30, "city": "Los Angeles"},
        {"name": "Eve", "age": 35, "city": "San Francisco"},
    ]

    # Test 2: Using custom operator for a specific filter
    def custom_comparison(value, filter_value):
        return len(value["city"]) > len(filter_value)

    filter_dict = {"city": {"value": "Chicago", "operator": custom_comparison}}
    result = base_table.list(filter_dict)
    assert result == [
        {"name": "John", "age": 25, "city": "New York"},
        {"name": "Alice", "age": 30, "city": "Los Angeles"},
    ]

    # Test 3: Using multiple filters with basic and custom operators and sorting by name in ascending order
    filter_dict = {
        "age": {"value": 30, "operator": ">="},
        "city": {"value": "New York", "operator": "!="},
        "name": {"value": "Bob", "operator": custom_comparison},
    }
    result = base_table.list(filter_dict, order_column="name", order_direction="asc")
    assert result == [
        {"name": "Alice", "age": 30, "city": "Los Angeles"},
        {"name": "Eve", "age": 35, "city": "San Francisco"},
        {"name": "John", "age": 25, "city": "New York"},
    ]


# Test AgentsTable.list method with specific filter conditions
def test_agents_table_list():
    agents_table = create_agents_table()

    # Test: Using agent_type filter
    filter_dict = {"agent_type": {"value": "employee", "operator": "=="}}
    result = agents_table.list(filter_dict)
    assert result == []  # Assuming there are no agents of type 'employee'


# Test MessagesTable.list method with specific order conditions
def test_messages_table_list():
    messages_table = create_messages_table()

    # Test: Sorting by timestamp in descending order
    result = messages_table.list(order_column="timestamp", order_direction="desc")
    assert (
        result == data_list[::-1]
    )  # Assuming data_list is sorted by 'timestamp' in ascending order


# Test UsersTable.list method with no filter and specific order conditions
def test_users_table_list():
    users_table = create_users_table()

    # Test: Sorting by username in ascending order
    result = users_table.list(order_column="username", order_direction="asc")
    assert (
        result == data_list
    )  # Assuming data_list is sorted by 'username' in ascending order


# Test AgentsTable.add, AgentsTable.get, AgentsTable.update, and AgentsTable.delete methods
def test_agents_table_crud():
    agents_table = create_agents_table()

    # Test add method
    agent_data = {"agent_type": "employee", "name": "John Doe", "age": 30}
    agent_id = agents_table.add(agent_data)
    assert agent_id is not None

    # Test get method
    retrieved_data = agents_table.get(agent_id)
    assert retrieved_data == agent_data

    # Test update method
    updated_data = {"name": "Jane Doe"}
    agents_table.update(agent_id, updated_data)
    retrieved_data = agents_table.get(agent_id)
    assert retrieved_data["name"] == "Jane Doe"

    # Test delete method
    agents_table.delete(agent_id)
    retrieved_data = agents_table.get(agent_id)
    assert retrieved_data is None


# Test MessagesTable.add, MessagesTable.get, MessagesTable.update, and MessagesTable.delete methods
def test_messages_table_crud():
    messages_table = create_messages_table()

    # Test add method
    message_data = {"text": "Hello, World!", "timestamp": "2023-08-01 12:00:00"}
    message_id = messages_table.add(message_data)
    assert message_id is not None
