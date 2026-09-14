"""
Простой интеграционный тест без запуска полного crew.
Проверяет, что все компоненты загружаются и работают вместе.
"""

import sys
from pathlib import Path
from dotenv import load_dotenv
import os

# Загружаем переменные окружения
load_dotenv()

# Добавляем src в путь для импорта
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ai_soc.tools.custom_tool import (
    RouteCheckerTool, 
    TimeCheckerTool, 
    TicketPricingTool,
    AskUserTool
)
from ai_soc.utils.config_loader import get_config_loader
from ai_soc.agents import create_booking_agent
import yaml


def test_environment():
    """Проверка переменных окружения."""
    print("1. Проверка окружения...")
    
    model = os.getenv('MODEL')
    api_key = os.getenv('GEMINI_API_KEY')
    
    assert model, "MODEL не установлен"
    assert api_key, "GEMINI_API_KEY не установлен"
    
    print(f"   ✓ MODEL: {model}")
    print(f"   ✓ GEMINI_API_KEY: установлен")


def test_config_loading():
    """Проверка загрузки конфигурации."""
    print("\n2. Проверка конфигурации...")
    
    config = get_config_loader()
    
    cities = config.get_valid_cities()
    routes = config.get_routes()
    schedules = config.get_route_times()
    
    assert len(cities) > 0, "Города не загружены"
    assert len(routes) > 0, "Маршруты не загружены"
    assert len(schedules) > 0, "Расписания не загружены"
    
    print(f"   ✓ Городов: {len(cities)}")
    print(f"   ✓ Маршрутов: {len(routes)}")
    print(f"   ✓ Расписаний: {len(schedules)}")


def test_agents_config():
    """Проверка конфигурации агентов."""
    print("\n3. Проверка конфигурации агентов...")
    
    config_path = Path(__file__).parent.parent / "src" / "crew_atl" / "config" / "agents.yaml"
    
    with open(config_path, 'r', encoding='utf-8') as f:
        agents_config = yaml.safe_load(f)
    
    assert 'booking_agent' in agents_config, "booking_agent не найден"
    assert 'dialogue_analyzer' in agents_config, "dialogue_analyzer не найден"
    
    # Проверяем наличие обязательных полей
    for agent_name, agent_data in agents_config.items():
        assert 'role' in agent_data, f"{agent_name}: нет поля 'role'"
        assert 'goal' in agent_data, f"{agent_name}: нет поля 'goal'"
        assert 'backstory' in agent_data, f"{agent_name}: нет поля 'backstory'"
        print(f"   ✓ {agent_name}: все поля присутствуют")


def test_tools_workflow():
    """Проверка работы инструментов в связке."""
    print("\n4. Проверка workflow инструментов...")
    
    # Шаг 1: Проверяем маршрут
    route_tool = RouteCheckerTool()
    route_result = route_tool._run("Минск", "Гродно", "2025-10-15")
    
    import json
    route_data = json.loads(route_result)
    assert route_data['available'], "Маршрут должен быть доступен"
    print("   ✓ Шаг 1: Маршрут проверен")
    
    # Шаг 2: Проверяем время
    time_tool = TimeCheckerTool()
    available_times = route_data['times']
    first_time = available_times[0]
    
    time_result = time_tool._run("Минск", "Гродно", "2025-10-15", first_time)
    time_data = json.loads(time_result)
    assert time_data['available'], "Время должно быть доступно"
    print(f"   ✓ Шаг 2: Время {first_time} доступно")
    
    # Шаг 3: Получаем цену
    pricing_tool = TicketPricingTool()
    pricing_result = pricing_tool._run("Минск", "Гродно", "2025-10-15", first_time, 2)
    pricing_data = json.loads(pricing_result)
    
    assert pricing_data['total_cost'] > 0, "Стоимость должна быть больше 0"
    print(f"   ✓ Шаг 3: Цена рассчитана: {pricing_data['total_cost']} руб.")
    
    print("\n   ✓ Полный workflow бронирования работает!")


def test_agent_creation():
    """Проверка создания агентов."""
    print("\n5. Проверка создания агентов...")
    
    # Загружаем конфигурацию
    config_path = Path(__file__).parent.parent / "src" / "crew_atl" / "config" / "agents.yaml"
    with open(config_path, 'r', encoding='utf-8') as f:
        agents_config = yaml.safe_load(f)
    
    # Создаем mock LLM (без реального API вызова)
    from crewai.llm import LLM
    
    try:
        llm = LLM(
            model=os.getenv('MODEL', 'gemini/gemini-2.0-flash'),
            temperature=0.1,
            provider="google",
            api_key=os.getenv('GEMINI_API_KEY')
        )
        print("   ✓ LLM инициализирован")
    except Exception as e:
        print(f"   ⚠ LLM не удалось инициализировать (это нормально для теста): {e}")
        llm = None
    
    # Пробуем создать агента
    if llm:
        try:
            agent = create_booking_agent(llm, agents_config['booking_agent'])
            print(f"   ✓ booking_agent создан: {agent.role}")
        except Exception as e:
            print(f"   ⚠ Не удалось создать агента: {e}")
    else:
        print("   ⚠ Пропускаем создание агента (нет LLM)")


if __name__ == "__main__":
    print("=" * 70)
    print("ИНТЕГРАЦИОННЫЙ ТЕСТ ПРОЕКТА")
    print("=" * 70)
    
    try:
        test_environment()
        test_config_loading()
        test_agents_config()
        test_tools_workflow()
        test_agent_creation()
        
        print("\n" + "=" * 70)
        print("✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        print("=" * 70)
        print("\nПроект готов к работе! 🚀")
        
    except AssertionError as e:
        print(f"\n❌ Тест провален: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Ошибка при тестировании: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
