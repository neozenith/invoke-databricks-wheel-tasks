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
    """Run pytest with integration tests that use a test Databricks workspace."""
    # Run normal unit tests and append integration test coverage.
    c.run("python3 -m pytest")

    # NOTE: Can not run poetry as a subprocess within a running pytest process that is also using subprocess coverage checking. It interferes in unsupported ways.
    with c.cd("tests/example_databricks_project"):
        c.run("poetry -vvv build -f wheel --no-ansi")

    c.run("python3 -m pytest -m integration --cov-append")


@task
def docs(c):
    """Automate documentation tasks."""
    c.run("md_toc --in-place github --header-levels 4 README.md")
    # TODO: Add Sphinx docs generation here too.
