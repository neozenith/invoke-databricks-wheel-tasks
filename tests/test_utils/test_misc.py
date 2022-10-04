# Third Party
import pytest

# Our Libraries
from invoke_databricks_wheel_tasks.utils.misc import dict_from_keyvalue_list, tidy


def test_tidy():
    # Given
    input_text = """
        This is an example triple quoted string with leading spaces from running on multiple lines.
    """

    # When
    output_text = tidy(input_text)

    # Then
    assert output_text == "This is an example triple quoted string with leading spaces from running on multiple lines."
    assert output_text != input_text


class TestDictFromKeyValueList:

    # Parametrized Testing Scenarios
    dict_from_keyvalue_list_test_cases = {
        "empty": ([], None),
        "single": (["key1=value1"], {"key1": "value1"}),
        "many": (["key1=value1", "key2=value2"], {"key1": "value1", "key2": "value2"}),
        "duplicate": (["key1=value1", "key1=value2"], {"key1": "value2"}),
    }

    @pytest.mark.parametrize(
        "test_case,expectation",
        dict_from_keyvalue_list_test_cases.values(),
        ids=dict_from_keyvalue_list_test_cases.keys(),
    )
    def test_dict_from_keyvalue_list(self, test_case, expectation):
        # Given
        # test_case

        # When
        result = dict_from_keyvalue_list(test_case)

        # Then
        assert result == expectation
