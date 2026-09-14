from crewai import Agent
from typing import Any, Dict


def create_dialogue_analyzer(llm, config: Dict[str, Any]) -> Agent:
    return Agent(
        config=config,  # type: ignore[arg-type]
        tools=[],
        llm=llm,
        verbose=True,
    )


