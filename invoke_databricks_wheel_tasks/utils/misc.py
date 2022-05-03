# Standard Library
import json
import re
from typing import Any, Dict, List, Optional

# Third Party
import jinja2
from invoke.vendor import yaml3 as yaml


def tidy(text: str) -> str:
    """Tidy up f-string internal whitespace."""
    pattern = re.compile(
        """
            \\s{2,} # Detect all duplicate whitespace
        """,
        re.X,
    )
    return re.sub(pattern, "", text)


def dict_from_keyvalue_list(args: Optional[List[str]] = None) -> Optional[Dict[str, str]]:
    """Convert a list of 'key=value' strings into a dictionary."""
    return {k: v for k, v in [x.split("=") for x in args]} if args else None


def merge_template(template_filename: str, config: Optional[Dict[str, Any]]) -> str:
    """Load a Jinja2 template from file and merge configuration."""
    # Step 1: get raw content as a string
    with open(template_filename) as f:
        raw_content = f.read()

    # Step 2: Treat raw_content as a Jinja2 template if providing configuration
    if config:
        content = jinja2.Template(raw_content).render(**config)
    else:
        content = raw_content

    return content


def load_config(filename: str, environment_variables: Optional[Dict[str, str]] = None) -> Any:
    """Detect if file is JSON or YAML and return parsed datastructure.

    When environment_variables is provided, then the file is first treated as a Jinja2 template.
    """
    # Step 1 & 2: Get raw template string and merge config (as necessary), returning as string
    content = merge_template(filename, environment_variables)

    # Step 3: Parse populated string into a data structure.
    if filename.endswith("json"):
        return json.loads(content)
    elif any([filename.lower().endswith(ext) for ext in ["yml", "yaml"]]):
        return yaml.safe_load(content)

    raise ValueError(f"File type of {filename} not supported.")
