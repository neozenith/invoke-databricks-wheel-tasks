# Third Party
"""This test suite tests both load_config and merge_template but they are closely related.

It will look in fixtures/misc for folders named scenario-* where * is the name of the test scenario.
Each folder contains 4 files related for a test scenario.
Each collection will be loaded and prepared as a paraemtrized test case.
"""

# Standard Library
import json
import os
from pathlib import Path

# Third Party
import pytest

# Our Libraries
from invoke_databricks_wheel_tasks.utils.misc import (
    dict_from_keyvalue_list,
    load_config,
    merge_template,
)


def __list_test_scenarios():
    """Look in fixtures/misc for folders named scenario-* where * is the name of the test scenario."""
    return {
        Path(x[0]).name.replace("scenario-", ""): Path(x[0])
        for x in os.walk(Path("./tests/test_utils/fixtures/misc/"))
        if Path(x[0]).name.startswith("scenario-")
    }


def __load_test_scenarios():
    return {
        scenario_name: (
            scenario_path,
            # Environment Variables
            (scenario_path / "args.env").read_text().splitlines(),
            # Dynamically find files called config regardless of extension
            # Technically config files are also Jinja templates
            [scenario_path / f for x in os.walk(scenario_path) for f in x[2] if f.startswith("config.")][0],
            # Template File
            scenario_path / "template.json.j2",
            # Expcted merged output
            (scenario_path / "output.json").read_text(),
        )
        for scenario_name, scenario_path in __list_test_scenarios().items()
    }


@pytest.mark.parametrize(
    "fixture_path,env_args,config_path,template_path,expected_output",
    __load_test_scenarios().values(),
    ids=__load_test_scenarios().keys(),
)
def test_scenarios(fixture_path, env_args, config_path, template_path, expected_output):
    # Given
    env = dict_from_keyvalue_list(env_args)

    # When
    conf = load_config(str(config_path), env)
    output = merge_template(str(template_path), conf)

    # Then
    # Compare semantic output, not the exact string output.
    output_json = json.loads(output)
    expected_output_json = json.loads(expected_output)

    assert output_json == expected_output_json
