"""Arguments parsing."""
# Standard Library
from argparse import ArgumentParser, ArgumentTypeError
from typing import List


def cli_bool(bool_string):
    """Custom argpase type handler to convert booleanish strings to booleans.

    For more details about custom argparse types see below:
    https://docs.python.org/3/library/argparse.html#type
    """
    b = bool_string.lower()
    truthy = ["1", "t", "true", "y", "yes", "on"]
    falsey = ["0", "f", "false", "n", "no", "off"]

    if b in truthy:
        return True
    elif b in falsey:
        return False
    else:
        raise ArgumentTypeError(
            f"Unexpected value '{bool_string}', it was not in the lists of known truthy/falsey values: {truthy} or {falsey}"
        )


def parse_args(args: List[str]) -> dict:
    """Parse arguments in a structured way.

    valid_args - keys are the --key passed at the command line.
               - values are dicts of kwargs passed to ArgumentParser.add_argument
               - If the value is not a dict it is assumed to be equivalent of {"default": <value>}
    """
    valid_args = {
        "required_string_value": {"required": True},
        "optional_error_message_value": "",
        "should_throw_test_error": {"default": "False", "type": cli_bool},
    }

    parser = _arg_parse_builder(valid_args)

    return _post_process_args(vars(parser.parse_args(args)))


def _arg_parse_builder(arg_config: dict) -> ArgumentParser:
    """Helper to take a neat datastructure to build an ArgumentParser."""
    parser = ArgumentParser()

    for k, v in arg_config.items():
        key = f"--{k.replace('_', '-')}"
        properties = v if type(v) == dict else {"default": v}
        parser.add_argument(key, **properties)

    return parser


def _post_process_args(args: dict) -> dict:
    """Handle any post processing of arguments."""
    return args
