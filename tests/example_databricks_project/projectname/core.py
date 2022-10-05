# Standard Library
import sys
from typing import Any, Dict

# Third Party
from pyspark.sql import SparkSession

from .args import parse_args
from .exceptions import FakeDatabricksException


def main():
    """Entrypoint for running as a module or a Databricks job."""
    spark = SparkSession.builder.getOrCreate()

    # Hook into underlying log4j logger
    log4jLogger = spark._jvm.org.apache.log4j
    logger = log4jLogger.LogManager.getLogger(__name__)
    logger.setLevel(log4jLogger.Level.WARN)

    parsed_args = parse_args(list(sys.argv)[1:])

    my_spark_program(spark, parsed_args)


def my_spark_program(spark: SparkSession, args: Dict[str, Any]):
    """Main entrypoint for Spark job.

    This method is separated to make local testing with pytest easier
    by passing in the SparkSession from a fixture instead.
    """
    print(args)

    print(f"Hello {args['required_string_value']}!")

    if args["should_throw_test_error"]:
        raise FakeDatabricksException(args["optional_error_message_value"])

    # TODO: test a more complex workflow that runs spark.sql(...) transforms given a path to a *.sql.j2 Jinja sql template.
    # Attempt to recreate Jaffleshop example from dbt-labs.
