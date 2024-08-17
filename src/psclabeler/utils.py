"""Utilities or functions that are useful across all the different
modules in this package can be defined here."""

import logging
import logging.config

import yaml

logger = logging.getLogger(__name__)


def setup_logging(
    logging_config_path="./conf/base/logging.yml", default_level=logging.INFO
) -> None:
    """Set up configuration for logging utilities.

    Args:
        logging_config_path (str, optional): Defaults to "./conf/base/logging.yml".
        default_level (logging.constant, optional): Defaults to logging.INFO.
    """
    try:
        with open(logging_config_path, "rt", encoding="utf-8") as file:
            log_config = yaml.safe_load(file.read())
        logging.config.dictConfig(log_config)

    except Exception as error:
        logging.basicConfig(
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            level=default_level,
        )
        logger.error(error)
        logger.info("Logging config file is not found. Basic config is being used.")
