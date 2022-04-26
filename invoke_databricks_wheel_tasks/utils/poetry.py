# Standard Library
from functools import lru_cache
from pathlib import Path

# Third Party
from poetry.core.factory import Factory
from poetry.core.masonry.builders.wheel import WheelBuilder
from poetry.core.poetry import Poetry


@lru_cache(maxsize=None)
def poetry_project() -> Poetry:
    """Get an instance of the current Poetry project.

    This is cached so that subsequent calls in the same invoke session reduce interactions with disk.
    """
    poetry = Factory().create_poetry(Path(".").resolve())
    return poetry


@lru_cache(maxsize=None)
def poetry_project_name() -> str:
    """Get the name of the current Poerty project."""
    return str(poetry_project().pyproject.poetry_config["name"])


@lru_cache(maxsize=None)
def poetry_project_version() -> str:
    """Get the version of the current Poerty project."""
    return str(poetry_project().pyproject.poetry_config["version"])


@lru_cache(maxsize=None)
def poetry_wheel_builder() -> WheelBuilder:
    """Get poetry WheelBuilder instance."""
    return WheelBuilder(poetry_project())


@lru_cache(maxsize=None)
def poetry_wheelname() -> str:
    """Get poetry properly formatted wheelname from WheelBuilder instance."""
    builder = poetry_wheel_builder()
    return str(builder.wheel_filename)
