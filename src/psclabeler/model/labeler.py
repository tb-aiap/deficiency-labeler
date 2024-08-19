"""Module for building PSCInspector labeler."""

import logging
import os
from abc import ABC, abstractmethod

import omegaconf
from langchain_core.messages.base import BaseMessage
from langchain_core.prompts import PromptTemplate
from langchain_core.prompts.few_shot import FewShotPromptTemplate
from langchain_openai import AzureChatOpenAI
from langchain_openai.chat_models.base import BaseChatOpenAI

import psclabeler as psc

logger = logging.getLogger(__name__)


def azure_chat_model(params: omegaconf.DictConfig) -> BaseChatOpenAI:
    """Creates AzureChatOpenAI Chatmodel with params as kwargs into ChatModel.

    Args:
        params (omegaconf.DictConfig): Params such as temperature.

    Raises:
        ValueError: If no API_KEY is found in environment variables.

    Returns:
        BaseChatModel: ChatModel
    """
    if not os.getenv("AZURE_OPENAI_API_KEY"):
        logger.error("No API key detected in environment variable.")
        raise ValueError(
            "No API key found. Please set your AZURE_OPENAI_API_KEY in the .env file."
        )

    return AzureChatOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("AZURE_API_VERSION"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        deployment_name=os.getenv("AZURE_MODEL"),
        **params
    )


class PSCInspector(ABC):
    """Abstract method for labeler to rate each deficiency.

    Different PSCInspector should use this method for rating. Whether using
    zero-shot, few-shot or NLP context classifier."""

    @abstractmethod
    def rate_risk(deficiency_query: str):
        pass

    @property
    def risk_guideline(self):
        """Define risk guideline prompt for model."""
        self._risk_guideline = psc.model.prompt.RISK_ASSESSMENT
        return self._risk_guideline


class ZeroShotLLMPSCInspector(PSCInspector):
    """PSC Inspector that uses LLM for zero shot prompting."""

    def __init__(self, chat_model: BaseChatOpenAI) -> None:
        """Initialize PSCInspector with LLM."""
        self.model = chat_model

    @property
    def sys_prompt(self):
        """Define system prompt for model."""
        self._sys_prompt = psc.model.prompt.PSC_INSPECTOR
        return self._sys_prompt

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


class FewShotLLMPSCInspector(PSCInspector):
    """PSC Inspector that uses LLM with few shot prompting."""

    def __init__(self, chat_model: BaseChatOpenAI) -> None:
        """Initialize PSCInspector with LLM."""
        self.model = chat_model

    @property
    def few_shot_example_prompt(self):
        """Define system prompt for model."""
        self._example_prompt = psc.model.prompt.FEW_SHOT_EXAMPLES
        return self._example_prompt

    @property
    def few_shot_prompt_suffix(self):
        """Define suffix questions for few shot prompt."""
        self._few_shot_suffix = psc.model.prompt.FEW_SHOT_SUFFIX
        return self._few_shot_suffix

    def _create_few_shot_template(self) -> FewShotPromptTemplate:

        example_prompt = PromptTemplate(
            input_variables=["deficiency", "response"],
            template="{deficiency}\n{response}",
        )

        prompt = FewShotPromptTemplate(
            prefix=psc.model.prompt.PREFIX_PROMPT.format(
                risk_assessment=self.risk_guideline
            ),
            examples=self.few_shot_example_prompt,
            example_prompt=example_prompt,
            suffix=self.few_shot_prompt_suffix,
            input_variables=["input"],
        )

        return prompt

    def rate_risk(self, deficiency_query: str) -> BaseMessage:
        """Main method to rate risk for PSC report.

        Args:
            deficiency_query (str): A single PSC Report

        Returns:
            BaseMessage: Contains Messages of the inputs and outputs of ChatModels.
                response.content is the string content of the message.
        """
        self.prompt = self._create_few_shot_template()
        chain = self.prompt | self.model
        response = chain.invoke(input=deficiency_query)

        return response
