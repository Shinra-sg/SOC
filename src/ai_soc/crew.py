from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
import yaml
from .agents import create_booking_agent, create_dialogue_analyzer, create_testing_agent
from .agents.booking_agent import create_auto_booking_agent
import os
from crewai.llm import LLM
import time
from datetime import datetime
import pathlib

def get_llm() -> LLM:
    raw_model = os.getenv('MODEL') or "gemini/gemini-2.0-flash"
    model_name = raw_model.strip()
    if model_name.startswith("google/"):
        model_name = model_name.replace("google/", "gemini/", 1)
    if "/" not in model_name and model_name.startswith("gemini-"):
        model_name = f"gemini/{model_name}"
    for bad_suffix in ("-lite", "-exp"):
        if model_name.endswith(bad_suffix):
            model_name = model_name[: -len(bad_suffix)]
    if model_name.endswith("gemini-1.5-pro"):
        model_name = model_name.replace("gemini-1.5-pro", "gemini-1.5-pro")
    if not model_name or model_name == "gemini/":
        model_name = "gemini/gemini-2.0-flash"
    llm = LLM(
        model=model_name,
        temperature=0.1,
        provider="google",
        api_key=os.getenv('GEMINI_API_KEY'),
        max_retries=2,
        request_timeout=60
    )
    throttle_seconds = float(os.getenv('THROTTLE_SECONDS', '5'))
    original_call = llm.call

    def throttled_call(*args, **kwargs):
        if throttle_seconds > 0:
            time.sleep(throttle_seconds)
        return original_call(*args, **kwargs)

    llm.call = throttled_call  # type: ignore[assignment]
    return llm


@CrewBase
class AISocCrew():
    agents: List[BaseAgent]
    tasks: List[Task]
    
    def __init__(self):
        self.llm = get_llm()
        if not hasattr(self, 'agents_config'):
            self.agents_config = {}
        if not hasattr(self, 'tasks_config'):
            self.tasks_config = {}
        base = pathlib.Path(__file__).resolve().parent
        (base / "logs" / "dialogues").mkdir(parents=True, exist_ok=True)
        (base / "logs" / "analysis").mkdir(parents=True, exist_ok=True)
        config_dir = base / "config" / "agents"
        merged = {}
        for p in [config_dir / "booking_agent.yaml", config_dir / "dialogue_analyzer.yaml", config_dir / "testing_agent.yaml"]:
            if p.exists():
                with open(p, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f) or {}
                    merged.update(data)
        try:
            self.agents_config.update(merged)  # type: ignore[attr-defined]
            print(f"DEBUG: Загружены агенты: {list(merged.keys())}")
        except Exception as e:
            print(f"DEBUG: Ошибка загрузки конфигурации: {e}")
            self.agents_config = self.agents_config or {}
    @agent
    def booking_agent(self) -> Agent:
        return create_booking_agent(self.llm, self.agents_config['booking_agent']) # type: ignore[index]

    @agent
    def dialogue_analyzer(self) -> Agent:
        return create_dialogue_analyzer(self.llm, self.agents_config['dialogue_analyzer']) # type: ignore[index]

    @agent
    def testing_agent(self) -> Agent:
        base = pathlib.Path(__file__).resolve().parent
        config_path = base / "config" / "agents" / "testing_agent.yaml"
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        return create_testing_agent(self.llm, config['testing_agent']) # type: ignore[index]
    @task
    def booking_dialogue_task(self) -> Task:
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        base = pathlib.Path(__file__).resolve().parent
        output_dir = base / "logs" / "dialogues"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"dialogue_{ts}.md"
        return Task(
            config=self.tasks_config['booking_dialogue_task'], # type: ignore[index]
            output_file=str(output_path),
        )

    @task
    def testing_task(self) -> Task:
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        base = pathlib.Path(__file__).resolve().parent
        output_dir = base / "logs" / "dialogues"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"dialogue_{ts}.md"
        return Task(
            config=self.tasks_config['testing_task'], # type: ignore[index]
            output_file=str(output_path),
        )

    @task
    def interactive_booking_task(self) -> Task:
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        base = pathlib.Path(__file__).resolve().parent
        output_dir = base / "logs" / "dialogues"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"dialogue_{ts}.md"
        return Task(
            config=self.tasks_config['interactive_booking_task'], # type: ignore[index]
            output_file=str(output_path),
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=[self.booking_agent()],
            tasks=[self.booking_dialogue_task()],
            process=Process.sequential,
            verbose=True,
        )

    def testing_crew(self) -> Crew:
        return Crew(
            agents=[self.testing_agent()],
            tasks=[self.testing_task()],
            process=Process.sequential,
            verbose=True,
        )

    def full_testing_crew(self) -> Crew:
        auto_booking_agent = create_auto_booking_agent(self.llm, self.agents_config['booking_agent']) # type: ignore[index]
        return Crew(
            agents=[auto_booking_agent],
            tasks=[self.interactive_booking_task()],
            process=Process.sequential,
            verbose=True,
        )
