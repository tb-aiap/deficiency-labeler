"""Unit test for data_query."""

import pytest

import psclabeler as psc


@pytest.fixture
def report_chunk():
    """Sample Report for chunk split test."""
    sample_text = """
    Deficienc y 1 
    Deficiency : Location of emergency installations. Not as required.   
    Preventive action: Ship Staff advised to fortify their inspection regime
    as per CLE 08 - Inactive Function tests, and rectify faults if any immediately.  
    Deficiency2 
    Deficiency : The loading computer used for Stability Calculation was not appro
    Root Cause: Work negligence for chief mate installed the loading computer device 
    Preventive action: 1. Master enhance supervision and training, supervis
    per SMS procedure. 2. Circulate to the fleet and require all ship Master 
    avoid the similar defect recurrence.  
    Deficiency 3 
    Deficiency : Alarms/Emergency Signal - At the engine room, Four light ala
    Preventive action: 1. Educate the crew to test the lights alarm signal co
    inspection in E/R. 2. Person in charge make the plan inspection."""
    return sample_text


def test_split_report_to_chunk_default(report_chunk):
    """Test default regex split the chunk as expected."""
    report_dict = psc.data_query.data_ingest.split_report_to_chunk(report_chunk)

    assert len(report_dict) == 3


def test_split_report_to_chunk_custom(report_chunk):
    """Test that a custom regex split the chunk as expected"""
    report_dict = psc.data_query.data_ingest.split_report_to_chunk(
        report_chunk,
        split_regx=r"Alarms/Emergency Signal",
    )
    assert len(report_dict) == 2


def test_split_report_to_chunk_no_split(report_chunk):
    """Test that regex with no match should not result in any split."""
    report_dict = psc.data_query.data_ingest.split_report_to_chunk(
        report_chunk,
        split_regx=r"zzzzzzzzzzzzzzzzzzzzzz",
    )
    assert len(report_dict) == 1
