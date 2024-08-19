"""Utilities or functions that are useful across all the different
modules in this package can be defined here."""

import logging
import logging.config
from importlib import import_module
from typing import Any

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


def load_func(dotpath: str):
    """Load function in module. Function name is right-most segment.

    Requires full library name.

    Example:
    A string value torch.nn.MSELoss
    module_ = torch.nn
    func_result = getattr(module, MSELoss)

    A string value numpy.sum / Does not work with np.sum
    module_ = numpy
    func_result = getattr(module, sum)
    """
    module_, func = dotpath.rsplit(".", maxsplit=1)
    try:
        m = import_module(module_)
        func_result = getattr(m, func)
    except AttributeError as e:
        logger.error(
            "Check spelling in config '{}' for Function - {}".format(dotpath, e)
        )
        raise AttributeError(e)
    except ModuleNotFoundError as e:
        logger.error("Check spelling in config '{}' for Module - {}".format(dotpath, e))
        raise ModuleNotFoundError(e)

    logger.debug("load_func returns result = {}".format(func_result))
    return func_result


def load_class_object(object_dotpath: str) -> Any:
    """Use string `object_dotpath` to create uninstantiated class object.

    Args:
        object_dotpath (str): dotpath to object.

    Example use:
    model = load_class_object()("init params goes here")
    model = load_class_object("psclabeler.model.labeler.LLMPSCInspector")(temperature=0)

    Returns:
        Any: A class that is uninstantiated.
    """
    try:
        class_object = load_func(object_dotpath)
        logger.info(f"Loading Uninstantiated Object: {class_object}")
        return class_object
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        raise
