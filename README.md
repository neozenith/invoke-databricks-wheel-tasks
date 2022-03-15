# Invoke Databricks Wheel Tasks

Databricks Python Wheel dev tasks in a namespaced collection of tasks to enrich the Invoke CLI task runner.

## Getting Started

```sh
pip install invoke-databricks-wheel-tasks
```

This will also install `invoke` and `databricks-cli`.

### Databricks CLI Config

It is assumed you will follow the documentation provided to setup `databricks-cli`.

https://docs.databricks.com/dev-tools/cli/index.html

You'll need to setup a Personal Access Token. Then run the following command:

```sh
databricks configure --profile yourprofilename --token

Databricks Host (should begin with https://): https://myorganisation.cloud.databricks.com/
Token: 
```

Which will create a configuration file in your home directory at `~/.databrickscfg` like:

```sh
cat ~/.databrickscfg

[yourprofilename]
host = https://myorganisation.cloud.databricks.com/
token = dapi0123456789abcdef0123456789abcdef
jobs-api-version = 2.1
```

### Invoke Setup

`tasks.py`

```python
from invoke import task, Collection, Tasks
import invoke_databricks_wheel_tasks as db

@task
def format(c):
    """Autoformat code for code style."""
    c.run("black .")
    c.run("isort .")

@task
def build(c):
    """Build wheel."""
    c.run("rm -rfv dist/")
    c.run("poetry build -f wheel")

# TODO: Find a neater way to capture root tasks as well as setting namespaces
ns = Collection(*[v for v in globals().values() if type(v) == Task])
ns.add_collection(db, name="db")
```

Once your `tasks.py` is setup like this `invoke` will have the extra commands:

```sh
λ invoke --list
Available tasks:

  format         Autoformat code for code style.
  build          Build wheel.
  db.runjob          Trigger default job associated for this project.
  db.reinstall   Reinstall version of wheel on cluster with a restart.
  db.upload      Upload wheel artifact to DBFS.
  db.clean       Clean wheel artifact from DBFS.
```

### Invoke Configuration

Each of the tasks will require some combination of `profile`, `cluster-id`, `job-id` etc.
You can create an `invoke.yaml` file which will get loaded into the `invoke` `Context` `Configuration`.

This will greatly simplify your typing by setting workspace specific flags for your dev iteration loop.

```yaml
# https://docs.pyinvoke.org/en/latest/concepts/configuration.html
databricks:
  profile: yourprofilename
  cluster-id: your-cluster-id-here
  job-id: 9999
  artifact-path: "dbfs:/FileStore/wheels/"
  wheel: "dbfs:/FileStore/wheels/projectname-0.1.0-py3-none-any.whl"
```

## The Tasks

### db.upload

This task will use `dbfs` to empty the upload path and then copy the built wheel from `dist/`.
This project assumes you're using `poetry` or your wheel build output is located in `dist/`.

If you have other requirements then _pull requests welcome_.

### db.clean

This tasks will clean up all items on the target `--artifact-path`.

### db.reinstall

After some trial and error, creating a job which creates a job cluster everytime is roughly 7 minutes.

However if you create an all purpose cluster that you:
 - Mark the old wheel for uninstall
 - restart cluster
 - install updated wheel from dbfs location
 
 This takes roughly 2 minutes which is a much tighter development loop. So these three steps are what `db.reinstall` performs.

### db.runjob

Assuming you have defined a job, that uses a pre-existing cluster, that has your latest wheel installed, this will create a manual trigger of your job with `job-id`.

The triggering returns a `run-id`, where this `run-id` gets polled until the state gets to an end state.

Then a call to `databricks runs get-output --run-id` happens to retrieve and `error`, `error_trace` and/or `logs` to be emitted to console.


## All Together

Assuming, you created your cluster and job definition you may want to create a root level `@task` like:

```python
@task(pre=[build, db.upload, db.reinstall, db.runjob], default=True)
def dev(c):
  """Default development loop."""
  ...
```

You will notice a few things here:

1. The method has no implementation `...`
1. We are chaining a series of `@task`s in the `pre=[...]` argument
1. The `default=True` on this root tasks means we could run either `invoke dev` or simply `invoke`.

How cool is that?


# Contributing

At all times, you have the power to fork this project, make changes as you see fit and then:

```sh
pip install https://github.com/user/repository/archive/branch.zip
```
[Stackoverflow: pip install from github branch](https://stackoverflow.com/a/24811490/622276)

That way you can run from your own custom fork in the interim or even in-house your work and simply use this project as a starting point. That is totally ok.

However if you would like to contribute your changes back, then open a Pull Request "across forks".

Once your changes are merged and published you can revert to the canonical version of `pip install`ing this package.

If you're not sure how to make changes or if you should sink the time and effort, then open an Issue instead and we can have a chat to triage the issue.


# Resources

 - [`pyinvoke`](https://pyinvoke.org)
 - [`databricks-cli`](https://docs.databricks.com/dev-tools/cli/index.html)

# Prior Art

 - https://github.com/Smile-SA/invoke-sphinx
 - https://github.com/Dashlane/dbt-invoke

