
import pytest
from AFAAS.interfaces.task.base import AbstractBaseTask



"""""
THE  FUNCTION print_tree(node, prefix="") IS USED TO PRINT A TREE STRUCTURE OF THE TESTS
"""""
def print_tree(node : AbstractBaseTask, prefix=""):
    # Print the current node's name
    print(prefix + "|-- " + node.debug_formated_str(status=True))

    # Check if the node has subtasks
    if node.subtasks:
        for i, child in enumerate(node.subtasks):
            # If the child is the last child, don't draw the vertical connector
            if i == len(node.subtasks) - 1:
                extension = "    "
            else:
                extension = "|   "
            # Recursively print each subtree, with an updated prefix
            print_tree(child, prefix + extension)


test_trees = {}


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """Add additional section in terminal summary reporting."""
    terminalreporter.write_sep("-", "Tree Structure for Tests")
    for test_name, tree in test_trees.items():
        terminalreporter.write(f"Tree for {test_name}:\n")
        print_tree(tree, file=terminalreporter) 


# Example test using the fixture
def example(plan_step_0):
    # Perform your test logic...
    # Store the tree for reporting
    assert 1 == 1
    test_trees["test_example"] = plan_step_0
