"""Unit test module for ReportWriter."""

from pathlib import Path
from unittest.mock import MagicMock

import omegaconf
import pandas as pd
import pytest

import psclabeler as psc


@pytest.fixture
def writer():
    """Writer objecet for unit test."""
    writer_objec = psc.report.writer.ExcelReportWriter
    return writer_objec


@pytest.fixture()
def pipeline_config(tmp_path):
    """Testing config for writer testing."""
    temp_dir = tmp_path / "data"
    temp_dir.mkdir()
    return omegaconf.OmegaConf.create(
        {
            "output_folder": temp_dir,
            "expected_df_columns": [
                "classification",
                "deficiency",
                "corrective action",
                "preventive action",
                "reason",
            ],
            "split_text_token": "\n\n",
        }
    )


@pytest.fixture()
def sample_response():
    """Testing text sample for writer testing."""
    response_text = [
        """Deficiency: this is a serious deficiency.\n\nReason: testdeficiency.
            \n\nClassification: Medium
            \n\nCorrective Action: Action 1\n\nPreventive Action: Action 1""",
        """Deficiency: this is a test deficiency.\n\n
        Reason:
        - The deficiency exposes a weakness in the organization's processes.
        - It is not significant enough to threaten human life or cause an accident.
        \n\n
        Classification: Medium\n\nCorrective Action: Action 1\n\nPreventive Action: Action 1
        """,
    ]
    return response_text


@pytest.fixture
def ai_response(sample_response):
    """Mock up AI Message for Report input"""

    response_1 = MagicMock()
    response_1.content = sample_response[0]
    response_1.response_metadata = {
        "token_usage": {
            "completion_tokens": 999,
            "prompt_tokens": 1493,
            "total_tokens": 1651,
        }
    }

    response_2 = MagicMock()
    response_2.content = sample_response[1]
    response_2.response_metadata = {
        "token_usage": {
            "completion_tokens": 158,
            "prompt_tokens": 1493,
            "total_tokens": 1651,
        }
    }

    ai_response = [response_1, response_2]

    return ai_response


def test_content_array_property(writer, pipeline_config, ai_response):
    """Test content array property method."""
    # arrange / act
    writer_obj = writer(ai_response, pipeline_config)

    # assert
    assert len(writer_obj.content_array) == 2
    assert isinstance(writer_obj.content_array[0], str)


def test_token_use_array_property(writer, pipeline_config, ai_response):
    """Test content array property method."""
    # arrange / act
    writer_obj = writer(ai_response, pipeline_config)
    response = writer_obj.token_use_array

    # assert
    assert isinstance(response, list)
    assert isinstance(response[0], dict)
    assert response[0]["completion_tokens"] == 999


def test_split_str_token(writer, pipeline_config, ai_response):
    """Test split str token changes with config."""
    # arrange / act
    writer_obj_1 = writer(ai_response, pipeline_config)

    pipeline_config["split_text_token"] = "aaa"
    writer_obj_2 = writer(ai_response, pipeline_config)

    # assert
    assert writer_obj_1.split_str_token == "\n\n"
    assert writer_obj_2.split_str_token == "aaa"


def test_parse_single_response_to_dict(writer, pipeline_config, ai_response):
    """Test parsing of single response to dict is as expected."""
    # arrange
    sample_single_response = [
        "Deficiency: this is a serious deficiency.",
        "Reason: testdeficiency",
        "Classification: Medium",
        "Corrective Action: Action 1",
        "Preventive Action: Action 1",
    ]
    # act
    writer_obj = writer(ai_response, pipeline_config)
    result = writer_obj._parse_single_response_to_dict(sample_single_response)

    # assert
    assert isinstance(result, dict)
    assert result["deficiency"]


def test_parse_report(writer, pipeline_config, ai_response):
    """Test parse_report method."""
    # arrange / act
    writer_obj = writer(ai_response, pipeline_config)
    result = writer_obj._parse_report()

    # assert
    assert isinstance(result, list)
    assert isinstance(result[0], dict)


def test_write_report(writer, pipeline_config, ai_response):
    """Test write_report method."""
    # arrange / act
    writer_obj = writer(ai_response, pipeline_config)
    writer_obj.write_report()

    # assert
    assert isinstance(writer_obj.report_df, pd.DataFrame)
    assert isinstance(writer_obj.metadata_df, pd.DataFrame)

    for s in pipeline_config["expected_df_columns"]:
        assert s in writer_obj.report_df.columns


def test_save_report(writer, pipeline_config, ai_response):
    """Test save_report method correctly saves excel file."""
    # arrange / act
    writer_obj = writer(ai_response, pipeline_config)
    writer_obj.write_report()
    writer_obj.save_report()

    # assert
    for i in Path(pipeline_config["output_folder"]).iterdir():
        assert i.suffix == ".xlsx"
