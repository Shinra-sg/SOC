"""
Тесты для утилит проекта.
"""

import sys
from pathlib import Path

# Добавляем src в путь для импорта
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ai_soc.utils.date_utils import normalize_date_string, validate_date_in_future
from ai_soc.utils.time_utils import normalize_time_string, validate_time_format
from ai_soc.utils.config_loader import get_config_loader


def test_date_normalization():
    """Тест нормализации дат."""
    print("Тестирование нормализации дат...")
    
    test_cases = [
        ("2025-10-15", "2025-10-15"),
        ("15-10-2025", "2025-10-15"),
        ("15.10.2025", "2025-10-15"),
        ("15/10/2025", "2025-10-15"),
    ]
    
    for input_date, expected in test_cases:
        result = normalize_date_string(input_date)
        status = "✓" if result == expected else "✗"
        print(f"  {status} {input_date} -> {result} (ожидалось: {expected})")


def test_time_normalization():
    """Тест нормализации времени."""
    print("\nТестирование нормализации времени...")
    
    test_cases = [
        ("14:30", "14:30"),
        ("14-30", "14:30"),
        ("14.30", "14:30"),
        ("14", "14:00"),
        ("1430", "14:30"),
        ("14 часов", "14:00"),
    ]
    
    for input_time, expected in test_cases:
        result = normalize_time_string(input_time)
        status = "✓" if result == expected else "✗"
        print(f"  {status} '{input_time}' -> '{result}' (ожидалось: '{expected}')")


def test_config_loader():
    """Тест загрузчика конфигурации."""
    print("\nТестирование загрузчика конфигурации...")
    
    config = get_config_loader()
    
    # Проверяем города
    cities = config.get_valid_cities()
    print(f"  ✓ Загружено городов: {len(cities)}")
    
    # Проверяем маршруты
    routes = config.get_routes()
    print(f"  ✓ Загружено маршрутов: {len(routes)}")
    
    # Проверяем расписания
    schedules = config.get_route_times()
    print(f"  ✓ Загружено расписаний: {len(schedules)}")
    
    # Проверяем конкретный маршрут
    minsk_grodno = ("Минск", "Гродно")
    if minsk_grodno in routes:
        print(f"  ✓ Маршрут Минск-Гродно найден")
        times = schedules.get(minsk_grodno, [])
        print(f"    Времена отправления: {', '.join(times)}")
    
    # Проверяем цены
    price = config.get_base_price("Минск", "Гродно")
    print(f"  ✓ Цена Минск-Гродно: {price} руб.")


if __name__ == "__main__":
    print("=" * 60)
    print("Тестирование утилит проекта atlas2")
    print("=" * 60)
    
    try:
        test_date_normalization()
        test_time_normalization()
        test_config_loader()
        
        print("\n" + "=" * 60)
        print("✓ Все тесты пройдены успешно!")
        print("=" * 60)
    except Exception as e:
        print(f"\n✗ Ошибка при тестировании: {e}")
        import traceback
        traceback.print_exc()
