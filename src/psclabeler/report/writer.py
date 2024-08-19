"""Writer module to output response from LLM."""

import logging
import time
from abc import ABC, abstractmethod
from pathlib import Path

import omegaconf
import pandas as pd
from langchain_core.messages.ai import AIMessage

logger = logging.getLogger(__name__)


class ReportWriter(ABC):
    """Abstract Base Class for ReportWrite pipeline."""

    @abstractmethod
    def _parse_report(self):
        """Implement this method to parse the response into a format suitable report."""
        pass

    @abstractmethod
    def write_report(self):
        """Implement this method to create the report."""
        pass

    @abstractmethod
    def save_report(self):
        """Implement this method to save the report in required format."""
        pass


class ExcelReportWriter(ReportWriter):
    """ReportWriter that outputs Excel Report from LLM results.

    Args:
        ReportWriter (_type_): Implements abstractmethods in ReportWriter as the interface
        for pipeline.
    """

    def __init__(
        self,
        response_array: list[AIMessage],
        params: omegaconf.DictConfig,
        report_name: str = "labeled_report",
    ) -> None:
        """Initialize attributes for ExcelReportWriter.

        Args:
            response_array (list[AIMessage]): list of AIMessage reponse object from LLM.
            params (omegaconf.DictConfig): writer params from yaml file.
            report_name (str, optional): Define report name. Defaults to "labeled_report".
        """
        self.response_array = response_array
        self.report_name = report_name
        self.output_folder = Path(params["output_folder"])
        self.expected_df_columns = params["expected_df_columns"]
        self.report_df = None
        self.metadata_df = None

        self._split_str_token = params["split_text_token"]
        self._content_array = None
        self._token_use_array = None

    def _parse_report(self) -> list[dict[str, str]]:
        """Parse response array from LLM into required format for writing.

        Returns:
            list[dict[str, str]]: array of dict[str, str] for input into pd.DataFrame.
        """
        self.results = []
        for res in self.content_array:
            split_response = res.split(self.split_str_token)
            parse_response = self._parse_single_response_to_dict(split_response)
            self.results.append(parse_response)
        return self.results

    def write_report(self) -> None:
        """Writes the report into dataframe suitable for saving.

        `report_df` only returns selected columns as dataframe.
        """
        self.results = self._parse_report()

        self.report_df = pd.DataFrame(self.results)
        self.report_df = self.report_df[self.expected_df_columns]

        self.metadata_df = pd.DataFrame(self.token_use_array)
        self.metadata_df = pd.concat([self.report_df, self.metadata_df], axis=1)

    def save_report(self):
        """Save the report into excel format with default or defined file_path.

        The file_name is appended with epochtime suffix to avoid duplication.

        Example:
            ".\data\labeled_report-1724075886.xlsx"
        """
        self._validate_columns()

        self.report_name += "-{:.0f}".format(time.time())
        self.report_name += ".xlsx"

        # create filepath for output, and create all folders to file if required.
        output_file_path = Path(self.output_folder, self.report_name)
        output_file_path.parent.mkdir(parents=True, exist_ok=True)

        logger.info("Saving report to {}".format(output_file_path))

        with pd.ExcelWriter(output_file_path.as_posix()) as writer:
            self.report_df.to_excel(writer, sheet_name="label_deficiency")
            self.metadata_df.to_excel(writer, sheet_name="token_output")

    @property
    def content_array(self) -> list[str]:
        """Content of LLM's response in a list of str for each Deficiency.

        Example:
        ["Deficiency: Fire extinguish is rusted.\n\nCorrective Action....",
        "Deficiency: Third mate is not familiar with log book....\n\nCorrective Action",
        "Deficiency: Invalid DOC certificate...\n\nCorrective Action",]
        """
        self._content_array = [r.content for r in self.response_array]
        return self._content_array

    @property
    def token_use_array(self) -> list[dict[str, str]]:
        """Return the metadata for token usage.

        Example: [
            {'completion_tokens': 163, 'prompt_tokens': 1466, 'total_tokens': 1629},
            {'completion_tokens': 158, 'prompt_tokens': 1493, 'total_tokens': 1651},
            {'completion_tokens': 135, 'prompt_tokens': 1435, 'total_tokens': 1570}
            ]
        """
        self._token_use_array = [
            r.response_metadata["token_usage"] for r in self.response_array
        ]
        return self._token_use_array

    @property
    def split_str_token(self) -> str:
        """Token to splits the entire content response from LLM into various category.

        Example:
            "Deficiency: some deficiency\n\n Corrective Action: some action \n\n Preventive
            Action: Some action \n\n"

            list output = [
                            "Deficiency: some deficiency",
                            "Corrective Action: some action",
                            "Preventive Action: Some action"
                            ]
        """
        return self._split_str_token

    @staticmethod
    def _parse_single_response_to_dict(response: list[str]) -> dict[str, str]:
        """After splitting each response into a list of 3 items, convert it into a dictionary.

        Get the response as a list of str, and parse it in to relevant key value pair.
        Args:
            response (list[str]): An array of single response string from LLM.

        Example of response.
        list output = [
                            "Deficiency: some deficiency",
                            "Corrective Action: some action",
                            "Preventive Action: Some action"
                            ]

        parsed output
        dict[str,str] output = {
                            "Deficiency" : "some deficiency",
                            "Corrective Action" : "some action",
                            "Preventive Action" : "Some action"
                            }


        Returns:
            dict[str, str]: _description_
        """
        split_k_v = [i.split(":", maxsplit=1) for i in response]
        return {i[0].lower(): i[1].strip() for i in split_k_v}

    def _validate_columns(self) -> None:
        """Check that required columns are in generated dataframe.

        Raises:
            ValueError: Raise when required column is not in the generated dataframe.
        """
        for col in self.expected_df_columns:
            if col not in self.report_df.columns:
                error_msg = f"""
                            Required column {col} is not in Dataframe.
                            Found the following cols: {self.report_df.columns}
                            """
                logger.error(error_msg)
                raise ValueError(error_msg)
