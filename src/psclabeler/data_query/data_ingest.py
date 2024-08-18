"""Module for ingesting and parsing ingested data."""

import logging
import re
from pathlib import Path

import pypdf

logger = logging.getLogger(__name__)


def parse_pdf_to_string(pdf_file: Path | str) -> str:
    """Get pdf reader and return the whole report as a string.

    Args:
        pdf_file (Path | str): file path to pdf report.

    Returns:
        str: a string of the whole report concated.
    """
    logger.debug("Retrieving file from {}".format(pdf_file))

    report_str = ""
    reader = pypdf.PdfReader(pdf_file)
    for i in range(len(reader.pages)):
        report_str += reader.pages[i].extract_text()
    return report_str


def split_report_to_chunk(
    report_text: str, split_regx: str = r"[Dd]eficienc.?y.?\d"
) -> dict[int, str]:
    """Parse a text of deficiency report into individual deficiency as a hash map.

    Splits the report by a expected formatting type.

    Args:
        report_text (str): string value of the deficiency report
        split_regx (str, optional): Split entire report into individual deficiency.
                                    Defaults to r"[Dd]eficienc.?y.?\d".

    Returns:
        dict[int, str]: dictionary of each deficiency as value in key,value pair.
    """
    deficiencies = re.split(split_regx, report_text)
    deficiencies = [d.strip() for d in deficiencies if d.strip()]

    logger.info("Found {} deficiencies in the report".format(len(deficiencies)))
    list_d = {}
    for i, deficiency in enumerate(deficiencies, 1):
        if deficiency:
            list_d[i] = f"{deficiency}"

    if len(list_d) == 1:
        logger.warning("There is no split in the report. Chunk size is 1")

    return list_d
