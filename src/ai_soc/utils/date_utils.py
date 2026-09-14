"""
Утилиты для работы с датами.
"""

from datetime import datetime, timedelta
from typing import Set


def normalize_date_string(date_str: str) -> str:
    """
    Нормализует строку даты в формат YYYY-MM-DD.
    
    Поддерживаемые форматы:
    - YYYY-MM-DD (2025-10-15)
    - DD-MM-YYYY (15-10-2025)
    - DD.MM.YYYY (15.10.2025)
    - YYYY.MM.DD (2025.10.15)
    - DD/MM/YYYY (15/10/2025)
    
    Args:
        date_str: Строка с датой в одном из поддерживаемых форматов
        
    Returns:
        Дата в формате YYYY-MM-DD или исходная строка если парсинг не удался
    """
    if not date_str:
        return date_str
    
    date_formats = [
        "%Y-%m-%d",  # 2025-10-15
        "%d-%m-%Y",  # 15-10-2025
        "%d.%m.%Y",  # 15.10.2025
        "%Y.%m.%d",  # 2025.10.15
        "%d/%m/%Y",  # 15/10/2025
    ]
    
    s = date_str.strip()
    for fmt in date_formats:
        try:
            dt = datetime.strptime(s, fmt)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            continue
    
    return date_str


def parse_date(date_str: str) -> datetime:
    """
    Парсит строку даты в объект datetime.
    
    Args:
        date_str: Строка с датой
        
    Returns:
        Объект datetime
        
    Raises:
        ValueError: Если дата не может быть распарсена
    """
    normalized = normalize_date_string(date_str)
    return datetime.strptime(normalized, "%Y-%m-%d")


def get_next_available_date(
    date_str: str, 
    blackout_dates: Set[str], 
    max_days: int = 14
) -> str:
    """
    Находит следующую доступную дату, пропуская заблокированные.
    
    Args:
        date_str: Начальная дата
        blackout_dates: Множество недоступных дат в формате YYYY-MM-DD
        max_days: Максимальное количество дней для поиска
        
    Returns:
        Следующая доступная дата в формате YYYY-MM-DD
    """
    current_date = parse_date(date_str)
    
    for _ in range(max_days):
        current_date = current_date + timedelta(days=1)
        candidate = current_date.strftime("%Y-%m-%d")
        if candidate not in blackout_dates:
            return candidate
    
    # Если не нашли в пределах max_days, возвращаем дату после последней проверки
    return (current_date + timedelta(days=1)).strftime("%Y-%m-%d")


def validate_date_in_future(date_str: str, allow_today: bool = True) -> bool:
    """
    Проверяет, что дата находится в будущем (или сегодня).
    
    Args:
        date_str: Строка с датой
        allow_today: Разрешать ли сегодняшнюю дату
        
    Returns:
        True если дата валидна, False иначе
    """
    try:
        date_obj = parse_date(date_str)
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        if allow_today:
            return date_obj >= today
        else:
            return date_obj > today
    except ValueError:
        return False
