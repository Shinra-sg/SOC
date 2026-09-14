"""
Тесты инструментов бронирования.
"""

import sys
from pathlib import Path
import json

# Добавляем src в путь для импорта
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ai_soc.tools.custom_tool import (
    RouteCheckerTool, 
    TimeCheckerTool, 
    TicketPricingTool
)


def test_route_checker():
    """Тест проверки маршрута."""
    print("Тестирование RouteCheckerTool...")
    
    tool = RouteCheckerTool()
    
    # Тест 1: Доступный маршрут
    result = tool._run(
        departure_city="Минск",
        arrival_city="Гродно",
        date="2025-10-15"
    )
    data = json.loads(result)
    
    status = "✓" if data.get("available") else "✗"
    print(f"  {status} Минск → Гродно: {data.get('message')}")
    if data.get("available"):
        print(f"    Доступные времена: {', '.join(data.get('times', []))}")
    
    # Тест 2: Недоступный маршрут
    result = tool._run(
        departure_city="Минск",
        arrival_city="Париж",
        date="2025-10-15"
    )
    data = json.loads(result)
    
    status = "✓" if not data.get("available") and data.get("reason") == "unknown_city" else "✗"
    print(f"  {status} Минск → Париж (неизвестный город): {data.get('reason')}")
    
    # Тест 3: Заблокированный город
    result = tool._run(
        departure_city="Минск",
        arrival_city="Москва",
        date="2025-10-15"
    )
    data = json.loads(result)
    
    status = "✓" if not data.get("available") and data.get("reason") == "blocked_city" else "✗"
    print(f"  {status} Минск → Москва (заблокирован): {data.get('reason')}")


def test_time_checker():
    """Тест проверки времени."""
    print("\nТестирование TimeCheckerTool...")
    
    tool = TimeCheckerTool()
    
    # Тест 1: Доступное время
    result = tool._run(
        departure_city="Минск",
        arrival_city="Гродно",
        date="2025-10-15",
        desired_time="11:30"
    )
    data = json.loads(result)
    
    status = "✓" if data.get("available") else "✗"
    print(f"  {status} Минск → Гродно в 11:30: {data.get('message')}")
    
    # Тест 2: Недоступное время (предложение ближайшего)
    result = tool._run(
        departure_city="Минск",
        arrival_city="Гродно",
        date="2025-10-15",
        desired_time="10:00"
    )
    data = json.loads(result)
    
    status = "✓" if not data.get("available") and data.get("suggested_time") else "✗"
    print(f"  {status} Минск → Гродно в 10:00: предложено {data.get('suggested_time')}")
    
    # Тест 3: Время в разных форматах
    test_times = ["14 часов", "14-30", "1430"]
    for time_input in test_times:
        result = tool._run(
            departure_city="Минск",
            arrival_city="Гродно",
            date="2025-10-15",
            desired_time=time_input
        )
        data = json.loads(result)
        normalized = data.get("time") or data.get("suggested_time", "N/A")
        print(f"  ✓ '{time_input}' → {normalized}")


def test_ticket_pricing():
    """Тест расчета цен."""
    print("\nТестирование TicketPricingTool...")
    
    tool = TicketPricingTool()
    
    # Тест 1: Известный маршрут с ценой
    result = tool._run(
        departure_city="Минск",
        arrival_city="Гродно",
        date="2025-10-15",
        time="11:30",
        passengers=2
    )
    data = json.loads(result)
    
    print(f"  ✓ Минск → Гродно, 2 пассажира")
    print(f"    Взрослый билет: {data.get('adult_price')} руб.")
    print(f"    Детский билет: {data.get('child_price')} руб.")
    print(f"    Итого: {data.get('total_cost')} руб.")
    
    # Тест 2: Маршрут с базовой ценой
    result = tool._run(
        departure_city="Минск",
        arrival_city="Березовка",
        date="2025-10-15",
        time="13:00",
        passengers=1
    )
    data = json.loads(result)
    
    print(f"  ✓ Минск → Березовка, 1 пассажир: {data.get('total_cost')} руб.")


if __name__ == "__main__":
    print("=" * 60)
    print("Тестирование инструментов бронирования")
    print("=" * 60)
    
    try:
        test_route_checker()
        test_time_checker()
        test_ticket_pricing()
        
        print("\n" + "=" * 60)
        print("✓ Все тесты инструментов пройдены успешно!")
        print("=" * 60)
    except Exception as e:
        print(f"\n✗ Ошибка при тестировании: {e}")
        import traceback
        traceback.print_exc()
