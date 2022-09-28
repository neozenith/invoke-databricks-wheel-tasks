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

There are 2 options config file or environment variables.

#### Config file

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

#### Environment Variables

On some CI systems it is better to export secrets into environment variables rather than have config files with secrets on CI servers.

Export the following and the `databricks-cli` will pick it up:

```ini
DATABRICKS_HOST=https://myorganisation.cloud.databricks.com/
DATABRICKS_TOKEN=dapi0123456789abcdef0123456789abcdef
DATABRICKS_JOBS_API_VERSION="2.1
```

### Invoke Setup

`tasks.py`

```python
from invoke import task
from invoke_databricks_wheel_tasks import * # noqa
```

Once your `tasks.py` is setup like this `invoke` will have the extra commands:

```sh
λ invoke --list
Available tasks:

  dbfs-wheel-path        Generate the target path (including wheelname) this wheel should be uploaded to.
  dbfs-wheel-path-root   Generate the target path (excluding wheelname) this wheel should be uploaded to.
  define-job             Generate templated Job definition and upsert by Job Name in template.
  poetry-wheel-name      Display the name of the wheel file poetry would build.
  run-job                Trigger default job associated for this project.
  upload                 Upload wheel artifact to DBFS.
```

## The Tasks

### upload

This task will use `dbfs` to empty the upload path and then copy the built wheel from `dist/`.
This project assumes you're using `poetry` or your wheel build output is located in `dist/`.

If you have other requirements then _pull requests welcome_.


### define-job

You may want to run `invoke --help define-job` to get the help documentation.

There are a few arguments that get abbreviated which we will explain before discussing how they work together.
 - `--jinja-template` or `-j`: This is a [Jinja2 Template](https://jinja.palletsprojects.com/en/3.1.x/) that must resolve to a valid [Databricks Jobs JSON payload](https://docs.databricks.com/dev-tools/api/latest/jobs.html#) spec.
 - `--config-file` or `-c`: This is either a JSON or YAML file to define the config, that gets used to parametrise the above `jinja-template`. This `config-file` can also be a Jinja template to inject values that can only be known at runtime like the git feature branch you are currently on. By default it is treated as a plain config file and not a Jinja Template unless `environment-variable` flags are specified (_see next_).
 - `--environment-variable` or `-e`: This flag can be repeated many times to specify multiple values. It takes a string in the `key=value` format. 
    - Eg `-e branch=$(git branch --show-current) -e main_wheel=$MAIN -e utils_wheel=$UTILS`

So an example command could look like:
```sh
invoke define-job \
    -j jobs/base-job-template.json.j2 \
    -c jobs/customer360-etl-job.yaml \
    -e branch=$(git branch --show-current) \
    -e main_whl=$(invoke dbfs-wheel-path) \
    -e utils_whl=$UTILS_DBFS_WHEEL_PATH
```

Then the `-e` values can get templated into `customer360-etl-job.yml`. Then that YAML file gets parsed and injected into `base-job-template.json.j2`

This will then check the list of Jobs in your workspace, see if a job with the same name exists already and perform a _create or replace job_ operation. This expects the `config-file` to have a key `name` to be able to cross check the list of existing jobs.

**The beauty is that the specifics of `config-file` and `jinja-template` is completely up to you.**

`config-file` is the minimal datastructure you need to configure `jinja-template` and you just use the [Jinja Control Structures](https://jinja.palletsprojects.com/en/3.1.x/templates/#list-of-control-structures) (`if-else`, `for-loop`, etc) to traverse it and populate `jinja-template`.

### run-job

This will create a manual trigger of your job with `job-id`.

The triggering returns a `run-id`, where this `run-id` gets polled until the state gets to an end state.

Then a call to `databricks runs get-output --run-id` happens to retrieve and `error`, `error_trace` and/or `logs` to be emitted to console.



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

