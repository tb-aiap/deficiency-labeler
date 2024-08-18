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

    Corrective Action: What is it.

    Preventive Action: What is it.

    Reason: 
    Analyze the Deficiency Step by Step before classification.
    Does it expose a weakness in organization's processes?
    Is it significant and potential threat to human life and cause accident or fire?


    Classification: Only reply one word. Do not explain further
    """
)

PREFIX_PROMPT = PromptTemplate.from_template(
    """ 
    Given the following risk assessment guidelines: 
    {risk_assessment}
    ---

    Analyse the deficiency and root cause below step by step
    And classify the deficiency accordingly to the risk level.
    ---

    Give your response in the following format:
    Deficiency: What is it.

    Corrective Action: What is it.

    Preventive Action: What is it.

    Reason: 
    Analyze the Deficiency Step by Step before classification.
    Does it expose a weakness in organization's processes?
    Is it significant and potential threat to human life and cause accident or fire?


    Classification: Only reply one word. Do not explain further
    """
)

FEW_SHOT_EXAMPLES = [
    {
        "deficiency": """
        Deficiency: Fire extinguisher for rescue boat rusted seriously.
        Root cause: Inappropriate storage Fire extinguisher was not protected from weather.
        Corrective action: Fire extinguisher replaced with a new extinguisher. The extinguisher is kept covered 
        for protection against weather.
        Preventive Action: Brieifing of entire ship staff carried out by Superintendent as to checks of rescue boat 
        equipment. Lessons learned shared with all the vessels in Fleet.

        Give your response in the following format:
        Deficiency: What is it.

        Corrective Action: What is it.

        Preventive Action: What is it.

        Reason: 
        Analyze the Deficiency Step by Step before classification.
        Does it expose a weakness in organization's processes?
        Is it significant and potential threat to human life and cause accident or fire?


        Classification: Only reply one word. Do not explain further
        """,
        "response": """
        deficiency: Fire extinguisher for rescue boat rusted seriously.

        Corrective Action: Fire extinguisher replaced with a new extinguisher. The extinguisher is kept covered 
        for protection against weather.

        Preventive Action: Brieifing of entire ship staff carried out by Superintendent as to checks of rescue boat 
        equipment. Lessons learned shared with all the vessels in Fleet.

        reason: This is a potential threat to human life and shipboard accident if a fire breaks down, and the extinguisher is not usable.
        Inapproriate storage of fire extinguisher is also a lapse in management procedure.

        clssification: High Risk.
""",
    },
    {
        "deficiency": """
        Deficiency: The company name on the DOC is not the same as on the CSR. The interim SMC and interim Security certificate have different company names to the DOC.
        Root cause: Company stated in CSR doc not same as the DOC. Master without fail to cross check trading certificate.
        Corrective action: Master w/o fail to cross check all trading certificates and to report Office in case of discrepancy. Shore base also to support to see to it all certificate issued in accordance of the requirement.
        Preventive action: Education (Education and Training) Briefing of master carried out for checking and keeping up to date all trading certificates.

        Give your response in the following format:
        Deficiency: What is it.

        Corrective Action: What is it.

        Preventive Action: What is it.

        Reason: 
        Analyze the Deficiency Step by Step before classification.
        Does it expose a weakness in organization's processes?
        Is it significant and potential threat to human life and cause accident or fire?


        Classification: Only reply one word. Do not explain further
        """,
        "response": """
        deficiency: The company name on the DOC is not the same as on the CSR. The interim SMC and interim Security certificate have different company names to the DOC.

        Corrective Action: Master w/o fail to cross check all trading certificates and to report Office in case of discrepancy. Shore base also to support to see to it all certificate issued in accordance of the requirement.

        Preventive Action: Education (Education and Training) Briefing of master carried out for checking and keeping up to date all trading certificates.

        reason: Improper certification is a weakness in the organization to maintain proper documentation. There is no immediate threath to human life or accident.

        clssification: Medium Risk.
""",
    },
    {
        "deficiency": """
        Deficiency: Third mate was forgotten to record fire and abandon drill in Nav Logbook.
        Root cause: Third mate was not familiar with special requirements of Nav logbook regarding drill record, 
        which issued by CHINA MSA.
        Corrective action: 1. Add abandon and fire drill in Nav Logbook at major event column.
        2. Training all crew regarding special requirement regarding drill record in Nav Logbook.
        Preventive action: 1. All drill record should be recorded in nav logbook after drill all complete.
        2. Master should supervise whether duty officer was recording properly.

        Give your response in the following format:
        Deficiency: What is it.

        Corrective Action: What is it.

        Preventive Action: What is it.

        Reason: 
        Analyze the Deficiency Step by Step before classification.
        Does it expose a weakness in organization's processes?
        Is it significant and potential threat to human life and cause accident or fire?


        Classification: Only reply one word. Do not explain further
        """,
        "response": """
        deficiency: Third mate was forgotten to record fire and abandon drill in Nav Logbook.

        Corrective Action: 1. Add abandon and fire drill in Nav Logbook at major event column.
        2. Training all crew regarding special requirement regarding drill record in Nav Logbook.

        Preventive Action: 1. All drill record should be recorded in nav logbook after drill all complete.
        2. Master should supervise whether duty officer was recording properly.

        reason: Third mate forgotten to record due to unfamiliarity of recording procedure. This is a lapse in adminstration but the drill is completed.
        There is no threat to human life or potential accident. 

        clssification: Low Risk.
""",
    },
]

FEW_SHOT_SUFFIX = """
Analyse the deficiency and root cause below step by step
And classify the deficiency accordingly to the risk level, High, Medium Low.

Deficiency: {input}
"""
