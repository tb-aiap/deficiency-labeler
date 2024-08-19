"""Main Pipeline for labeling a single deficiency report."""

import argparse
import logging
from pathlib import Path
from typing import Any, Callable, TypeAlias

import omegaconf
from dotenv import load_dotenv
from langchain_openai.chat_models.base import BaseChatOpenAI

import psclabeler as psc

# set up logging
psc.utils.setup_logging()
logger = logging.getLogger(__name__)

# type alias
report_parser: TypeAlias = psc.data_query.data_ingest.ReportParser
psc_inspector: TypeAlias = psc.model.labeler.PSCInspector
report_writer: TypeAlias = psc.report.writer.ReportWriter

# func alias
load_object: Callable[[str], Any] = psc.utils.load_class_object
load_chat: Callable[[omegaconf.DictConfig], BaseChatOpenAI] = (
    psc.model.labeler.azure_chat_model
)


def main(conf: omegaconf.DictConfig) -> None:
    """Main function for unlabeled inspection pdf and outputs a labeled report.

    Main workflow of the pipeline.
        ReportParser: reads the pdf and output a dict[int, str] for each deficiency.
        PSCInspector: uses the dict[int, str] to loop through each deficiency.
        ReportWriter: takes the output from PSCInspector and writes/save the content.

    Args:
        conf (omegaconf.DictConfig): yaml config to set class objects and params.

    Raises:
        FileNotFoundError: If the file path is wrong.
    """
    logger.info("Starting Pipeline to rate deficiency report.")

    load_dotenv()

    # get file path using argparse
    parser = argparse.ArgumentParser(
        description="Assign risk ratings for a deficiency report."
    )
    parser.add_argument("pdf_path", type=str, help="Path to the PDF file")

    args = parser.parse_args()
    pdf_path = Path(args.pdf_path)

    if not pdf_path.is_file():
        raise FileNotFoundError(f"{pdf_path.as_posix()} is not a valid file path")

    logger.info("Parsing report from {}.".format(pdf_path))
    parser: report_parser = load_object(conf["parser_dotpath"])(pdf_path)
    report_dict = parser.parse_report()

    logger.info("Starting rate_risk on deficiencies.")
    model: psc_inspector = load_object(conf["labeler_dotpath"])(
        load_chat(conf["chat_model"])
    )
    results = [model.rate_risk(v) for v in report_dict.values()]

    logger.info("Saving report")
    writer: report_writer = load_object(conf["writer_dotpath"])(results, conf["writer"])
    writer.write_report()
    writer.save_report()

    logger.info("Pipeline Completed")


if __name__ == "__main__":
    conf = omegaconf.OmegaConf.load("./conf/base/pipeline.yml")
    main(conf)
