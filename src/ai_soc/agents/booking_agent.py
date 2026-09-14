from crewai import Agent
from typing import Any, Dict
from ..tools.custom_tool import RouteCheckerTool, TimeCheckerTool, TicketPricingTool, AskUserTool, AutoAskUserTool


def create_booking_agent(llm, config: Dict[str, Any]) -> Agent:
    return Agent(
        config=config,  # type: ignore[arg-type]
        tools=[RouteCheckerTool(), TimeCheckerTool(), TicketPricingTool(), AskUserTool()],
        llm=llm,
        verbose=True,
    )

def create_auto_booking_agent(llm, config: Dict[str, Any]) -> Agent:
    return Agent(
        config=config,  # type: ignore[arg-type]
        tools=[RouteCheckerTool(), TimeCheckerTool(), TicketPricingTool(), AutoAskUserTool()],
        llm=llm,
        verbose=True,
    )


