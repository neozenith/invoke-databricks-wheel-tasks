# Third Party
from invoke import task
from invoke_common_tasks import *  # noqa

# Our Libraries
from invoke_databricks_wheel_tasks import *  # noqa

# NOTE: Invoke tasks files don't support mypy typechecking for the forseeable future
# They were looking at addressing it after Python2 EOL 01-01-2020 but there was a global pandemic.
# https://github.com/pyinvoke/invoke/issues/357


@task
def integration_test(c):
    """Run pytest with no integration tests."""
    c.run("python3 -m pytest -m integration")
