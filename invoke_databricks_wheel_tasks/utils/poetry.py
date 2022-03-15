# Standard Library
from functools import lru_cache


@lru_cache(maxsize=None)
def poetry_project():
    """Get an instance of the current Poetry project.

    This is cached so that subsequent calls in the same invoke session reduce interactions with disk.
    """
    # Standard Library
    from pathlib import Path

    # Third Party
    from poetry.core.factory import Factory

    poetry = Factory().create_poetry(Path(".").resolve())
    return poetry


@lru_cache(maxsize=None)
def poetry_project_name():
    """Get the name of the current Poerty project."""
    return poetry_project().pyproject.poetry_config["name"]


@lru_cache(maxsize=None)
def poetry_project_version():
    """Get the version of the current Poerty project."""
    return poetry_project().pyproject.poetry_config["version"]


@lru_cache(maxsize=None)
def poetry_wheel_builder():
    """Get poetry WheelBuilder instance."""
    # Third Party
    from poetry.core.masonry.builders.wheel import WheelBuilder

    builder = WheelBuilder(poetry_project())
    return builder


@lru_cache(maxsize=None)
def poetry_wheelname():
    """Get poetry properly formatted wheelname from WheelBuilder instance."""
    builder = poetry_wheel_builder()
    return builder.wheel_filename
