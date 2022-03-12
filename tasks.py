# Third Party
from invoke import Collection, Task, task
from invoke_common_tasks import build, ci, format, lint, test  # noqa

# Our Libraries
import invoke_databricks_wheel_tasks as db


@task(pre=[build, db.upload, db.reinstall, db.runjob], default=True)
def dev(c):
    """Default databricks flow."""
    ...


# Collect root tasks
ns = Collection(*[v for v in globals().values() if type(v) == Task])
ns.add_collection(db, name="db")
