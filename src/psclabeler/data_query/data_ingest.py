"""Module for ingesting and parsing ingested data."""

import logging
import re
from abc import ABC, abstractmethod
from pathlib import Path

import pypdf

logger = logging.getLogger(__name__)


class ReportParser(ABC):
    """Abstract Base Class for parsing Inspection Report PDF."""

    @abstractmethod
    def parse_report(self) -> dict[int, str]:
        """Implement this method to parse_report that is ready for LLM input.

        Required format is dict[int, str], where int is the deficiency number.
        While str is the entire deficiency.

        So 5 deficiency in a single report as follows.
        return {1: "deficiency 1......corrective...",
                2: "deficiency 2......corrective...",
                3: "deficiency 3......corrective...",
                4: "deficiency 4......corrective...",
                5: "deficiency 5......corrective...",
                }
        """
        pass


class SampleReportParser(ReportParser):
    """SampleReportParser for returning report chunk as string after reading from path."""

    def __init__(self, pdf_path: str | Path):
        """Initialize SampleReportParser with file_path attribute.

        Args:
            pdf_path (str | Path): file to pdf report.
        """
        if isinstance(pdf_path, str):
            pdf_path = Path(pdf_path)
        self.pdf_path = pdf_path

    def parse_report(self) -> dict[int, str]:
        """Main method to parse pdf report.

        Gets the pdf file path to parse it. And returns a dict[int, str].
        Refer to Abstract Base Class for more information on this method.

        Returns:
            dict[int, str]: data format expected by LLM in pipeline.
        """
        report_string = self.parse_pdf_to_string(self.pdf_path)
        report_dict = self.split_report_to_chunk(report_string)

        return report_dict

    @staticmethod
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

    @staticmethod
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
