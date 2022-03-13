# Third Party
from invoke import task
from invoke_common_tasks import build, ci, format, lint, test  # noqa

# Our Libraries
from invoke_databricks_wheel_tasks import reinstall, runjob, upload  # noqa


@task(pre=[build, upload, reinstall, runjob], default=True)
def dev(c):
    """Default databricks flow."""
    ...
