from crewai import Agent
from typing import Any, Dict
from ..tools.custom_tool import AskUserTool, UserResponseTool, LLMUserResponseTool, StressTestScenarioTool


def create_testing_agent(llm, config: Dict[str, Any]) -> Agent:
    return Agent(
        config=config,  # type: ignore[arg-type]
        tools=[AskUserTool(), UserResponseTool(), LLMUserResponseTool(), StressTestScenarioTool()],
        llm=llm,
        verbose=True,
    )
