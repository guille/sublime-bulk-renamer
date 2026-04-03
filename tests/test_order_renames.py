# pyright: basic
import unittest

from internal.order_renames import order_rename_graph


def apply_rename_operations(operations, initial_state):
    """Apply a sequence of rename operations to an initial state.

    Args:
        operations: List of (src, dst) tuples representing rename operations
        initial_state: Dict mapping original names to their current names

    Returns:
        Final state after applying all operations
    """
    state = initial_state.copy()
    for src, dst in operations:
        # Find what currently has the name 'src'
        current_src = None
        for name, current_name in state.items():
            if current_name == src:
                current_src = name
                break

        if current_src is not None:
            state[current_src] = dst

    return state


def generate_test_case(test_case):
    """Generate a test method from a test case dict"""

    def test_method(self):
        graph_in = test_case["in"]
        result = order_rename_graph(graph_in)

        # Build initial state: each name maps to itself
        all_names = set()
        for src, dst in graph_in:
            all_names.add(src)
            all_names.add(dst)
        initial_state = {name: name for name in all_names}

        # Apply the result from order_rename_graph
        final_state = apply_rename_operations(result, initial_state)

        # Verify that each source in graph_in ends up at its intended destination
        # For each (src, dst) in graph_in, the item that originally had name 'src'
        # should now have name 'dst'
        for src, dst in graph_in:
            # The item that originally had name 'src' should now be named 'dst'
            actual_dst = final_state[src]
            self.assertEqual(
                actual_dst,
                dst,
                f"Item that originally had name '{src}' now has name '{actual_dst}', "
                f"expected '{dst}'",
            )

    test_method.__name__ = f"test_{test_case['name']}"
    test_method.__doc__ = f"Test case: {test_case['name']}"
    return test_method


class TestOrderRenameGraph(unittest.TestCase):
    """Test harness for order_rename_graph function.

    To add a test case, simply append a dict to TEST_CASES with:
    - 'in': list of input tuples
    - 'out': list of expected output tuples
    - 'name': descriptive name for the test
    """

    # Define your test cases here as dictionaries
    TEST_CASES = [
        {
            "in": [("a", "b"), ("c", "d")],
            "name": "simple_case",
        },
        {
            "in": [("a", "b"), ("b", "c")],
            "name": "chain",
        },
        {
            "in": [("a", "b"), ("b", "a")],
            "name": "cycle",
        },
        {
            "in": [("a", "c"), ("b", "b"), ("c", "a")],
            "name": "longer_cycle",
        },
    ]


# Dynamically generate test methods from TEST_CASES
for test_case in TestOrderRenameGraph.TEST_CASES:
    pairs = test_case["in"]
    valid = len({x for x, _ in pairs}) == len(pairs) and len(
        {y for _, y in pairs}
    ) == len(pairs)
    if valid is False:
        raise AttributeError(
            f"Invalid test case {test_case['name']} has duplicated sources or destinations"
        )
    test_method = generate_test_case(test_case)
    setattr(TestOrderRenameGraph, test_method.__name__, test_method)


if __name__ == "__main__":
    unittest.main()
