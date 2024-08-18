"""Module for building PSCInspector labeler."""

import logging
import os
import sys
from abc import ABC, abstractmethod

import dotenv
from langchain_core.messages.base import BaseMessage
from langchain_openai import AzureChatOpenAI

sys.path.append("src")
import psclabeler as psc

dotenv.load_dotenv()

logger = logging.getLogger(__name__)


class PSCInspector(ABC):
    """Abstract method for labeler to rate each deficiency.

    Different PSCInspector should use this method for rating. Whether using
    zero-shot, few-shot or NLP context classifier."""

    @abstractmethod
    def rate_risk(deficiency_query: str):
        pass


class ZeroShotLLMPSCInspector(PSCInspector):
    """PSC Inspector that uses LLM for zero shot prompting."""

    def __init__(self) -> None:
        """Initialize PSCInspector with LLM."""
        self.model = AzureChatOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("AZURE_API_VERSION"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            deployment_name=os.getenv("AZURE_MODEL"),
        )

    @property
    def sys_prompt(self):
        """Define system prompt for model."""
        self._sys_prompt = psc.model.prompt.PSC_INSPECTOR
        return self._sys_prompt

    @property
    def risk_guideline(self):
        """Define risk guideline prompt for model."""
        self._risk_guideline = psc.model.prompt.RISK_ASSESSMENT
        return self._risk_guideline

    def rate_risk(self, deficiency_query: str) -> BaseMessage:
        """Main method to rate risk for PSC report.

        Args:
            deficiency_query (str): A single PSC Report

        Returns:
            BaseMessage: Contains Messages of the inputs and outputs of ChatModels.
                response.content is the string content of the message.
        """
        context_prompt = psc.model.prompt.ZERO_SHOT_PROMPT.format(
            risk_assessment=self.risk_guideline,
            deficiency_query=deficiency_query,
        )
        response = self.model.invoke(
            input=[self.sys_prompt, context_prompt], temperature=0
        )

        return response
