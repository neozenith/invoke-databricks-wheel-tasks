# Third Party
from invoke import Collection, Task, task

# Our Libraries
import invoke_databricks_wheel_tasks as db


@task
def format(c):
    """Autoformat code for code style."""
    c.run("black .")
    c.run("isort .")


@task
def lint(c):
    """Linting and style checking."""
    c.run("black --check .")
    c.run("isort --check .")
    c.run("flake8 .")


@task(pre=[format, lint])
def test(c):
    """Run test suite."""
    c.run("python3 -m pytest")


@task
def build(c):
    """Build wheel."""
    c.run("rm -rfv dist/")
    c.run("poetry build -f wheel")


@task(pre=[build, db.upload, db.reinstall, db.go], default=True)
def dev(c):
    """Default databricks flow."""
    ...


# Collect root tasks
ns = Collection(*[v for v in globals().values() if type(v) == Task])
ns.add_collection(db, name="db")
