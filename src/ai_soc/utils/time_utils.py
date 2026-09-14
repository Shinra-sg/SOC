"""
Утилиты для работы со временем.
"""

from typing import Optional, List


def normalize_time_string(time_str: str) -> str:
    """
    Нормализует строку времени в формат HH:MM.
    
    Поддерживаемые форматы:
    - "14:30" или "14-30" или "14.30"
    - "14" (преобразуется в "14:00")
    - "1430" (преобразуется в "14:30")
    - "14 часов" (преобразуется в "14:00")
    
    Args:
        time_str: Строка со временем
        
    Returns:
        Время в формате HH:MM или пустая строка если парсинг не удался
    """
    if not time_str:
        return ""
    
    # Очищаем строку от лишних слов
    raw = time_str.strip().lower()
    for word in ["часов", "час", "ровно", "около", "примерно"]:
        raw = raw.replace(word, "").strip()
    
    # Заменяем разделители на двоеточие
    normalized = raw.replace(" ", "").replace("-", ":").replace(".", ":")
    
    # Случай 1: Только число (например "14" -> "14:00")
    if normalized.isdigit() and len(normalized) <= 2:
        hour = int(normalized) % 24
        return f"{hour:02d}:00"
    
    # Случай 2: Число из 3-4 цифр без разделителей (например "1430" -> "14:30")
    if normalized.isdigit() and len(normalized) in (3, 4):
        hour = int(normalized[:-2]) % 24
        minute = int(normalized[-2:]) % 60
        return f"{hour:02d}:{minute:02d}"
    
    # Случай 3: Время с разделителем (например "14:30")
    if ":" in normalized:
        parts = normalized.split(":")
        if len(parts) >= 2 and parts[0].isdigit() and parts[1].isdigit():
            hour = int(parts[0]) % 24
            minute = int(parts[1]) % 60
            return f"{hour:02d}:{minute:02d}"
    
    return ""


def find_closest_time(target_time: str, available_times: List[str]) -> Optional[str]:
    """
    Находит ближайшее доступное время из списка.
    
    Args:
        target_time: Целевое время в формате HH:MM
        available_times: Список доступных времен в формате HH:MM
        
    Returns:
        Ближайшее время или None если список пуст
    """
    if not available_times:
        return None
    
    try:
        target_hour = int(target_time.split(':')[0]) if target_time else 0
    except (ValueError, IndexError):
        target_hour = 0
    
    return min(
        available_times, 
        key=lambda x: abs(int(x.split(':')[0]) - target_hour)
    )


def validate_time_format(time_str: str) -> bool:
    """
    Проверяет, что время имеет корректный формат HH:MM.
    
    Args:
        time_str: Строка со временем
        
    Returns:
        True если формат корректный, False иначе
    """
    if not time_str or ':' not in time_str:
        return False
    
    parts = time_str.split(':')
    if len(parts) != 2:
        return False
    
    try:
        hour = int(parts[0])
        minute = int(parts[1])
        return 0 <= hour < 24 and 0 <= minute < 60
    except ValueError:
        return False
