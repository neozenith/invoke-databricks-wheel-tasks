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

This tasks will use `dbfs` to empty the upload path and then copy the built wheel from `dist/`.
This project assumes you're using `poetry` or your wheel build output is located in `dist/`.

If you have other requirements then _pull requests welcome_.

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

Open an issue and lets have a chat to triage needs or concerns before you sink too much effort on a PR.

Or if you're pretty confident your change is inline with the direction of this project then go ahead and open that PR.

Or feel free to fork this project and rename it to your own variant. It's cool, I don't mind.

# Resources

 - [`pyinvoke`](https://pyinvoke.org)
 - [`databricks-cli`](https://docs.databricks.com/dev-tools/cli/index.html)

# Prior Art

 - https://github.com/Smile-SA/invoke-sphinx
 - https://github.com/Dashlane/dbt-invoke

