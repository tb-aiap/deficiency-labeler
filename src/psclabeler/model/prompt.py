"""Moduele for storing prompts."""

from langchain_core.messages import SystemMessage
from langchain_core.prompts import PromptTemplate

PSC_INSPECTOR = SystemMessage(
    content=(
        "You are a strict vessel safety inspector."
        "You analyze the deficiency of a vessel finding step by step."
    )
)

RISK_ASSESSMENT = """
Definition of each severity level has been given below.
High Risk Finding is a significant finding that poses a threat to personnel, the ship, or the
environment and has the potential to cause medium to large economic and reputational harm.

Medium risk Finding are those that could be viewed as weaknesses in the organization's processes,
procedures, or shipboard practices.

Low risk Finding: The findings are neither high nor medium risk; they are unlikely to result in an
accident and, if they do, are likely to cause only minor damage.
"""

ZERO_SHOT_PROMPT = PromptTemplate.from_template(
    """ 
    Given the following risk assessment guidelines: 
    {risk_assessment}
    ---

    Analyse the deficiency and root cause below step by step
    And classify the deficiency accordingly to the risk level.

    Deficiency: 
    {deficiency_query}.
    ---

    Give your response in the following format:
    Deficiency: What is it.

    Reason: 
    Analyze the Deficiency Step by Step before classification.
    Does it expose a weakness in organization's processes?
    Is it significant and potential threat to human life and cause accident or fire?


    Classification: Only reply one word. Do not explain further
    """
)
