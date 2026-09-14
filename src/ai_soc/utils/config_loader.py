"""
Утилита для загрузки конфигурационных данных из YAML файлов.
"""

import os
import yaml
from typing import Dict, List, Set, Tuple, Any
from pathlib import Path


class RouteConfigLoader:
    """Загрузчик конфигурации маршрутов, городов и расписаний."""
    
    def __init__(self, config_path: str | None = None):
        """
        Инициализация загрузчика конфигурации.
        
        Args:
            config_path: Путь к файлу конфигурации. Если None, используется путь по умолчанию.
        """
        if config_path is None:
            current_dir = Path(__file__).parent.parent
            config_path = current_dir / "config" / "routes_data.yaml"
        
        self.config_path = Path(config_path)
        self._config: Dict[str, Any] = {}
        self._load_config()
    
    def _load_config(self) -> None:
        """Загружает конфигурацию из YAML файла."""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self._config = yaml.safe_load(f) or {}
        except FileNotFoundError:
            raise FileNotFoundError(
                f"Файл конфигурации не найден: {self.config_path}"
            )
        except yaml.YAMLError as e:
            raise ValueError(f"Ошибка парсинга YAML файла: {e}")
    
    def get_valid_cities(self) -> List[str]:
        """Возвращает список доступных городов."""
        return self._config.get("cities", {}).get("valid", [])
    
    def get_blocked_cities(self) -> Set[str]:
        """Возвращает множество заблокированных городов."""
        blocked = self._config.get("cities", {}).get("blocked", [])
        return set(blocked)
    
    def get_routes(self) -> Set[Tuple[str, str]]:
        """
        Возвращает множество доступных маршрутов в формате (from, to).
        Учитывает двунаправленные маршруты.
        """
        routes = set()
        routes_config = self._config.get("routes", [])
        
        for route in routes_config:
            from_city = route.get("from")
            to_city = route.get("to")
            bidirectional = route.get("bidirectional", False)
            
            if from_city and to_city:
                routes.add((from_city, to_city))
                if bidirectional:
                    routes.add((to_city, from_city))
        
        return routes
    
    def get_route_times(self) -> Dict[Tuple[str, str], List[str]]:
        """
        Возвращает словарь расписаний по маршрутам.
        Ключ: (город_отправления, город_прибытия)
        Значение: список времен отправления
        """
        route_times = {}
        schedules = self._config.get("schedules", {})
        
        for route_key, times in schedules.items():
            # Разбираем ключ маршрута "Город1-Город2"
            if "-" in route_key:
                parts = route_key.split("-", 1)
                if len(parts) == 2:
                    from_city, to_city = parts[0].strip(), parts[1].strip()
                    route_times[(from_city, to_city)] = times
        
        return route_times
    
    def get_pricing_matrix(self) -> Dict[str, float]:
        """
        Возвращает матрицу цен для маршрутов.
        Ключ: "Город1-Город2" или "default" для базовой цены
        """
        return self._config.get("pricing", {})
    
    def get_blackout_dates(self) -> Set[str]:
        """Возвращает множество недоступных дат для бронирования."""
        dates = self._config.get("blackout_dates", [])
        return set(dates)
    
    def get_base_price(self, from_city: str, to_city: str) -> float:
        """
        Возвращает базовую цену для маршрута.
        
        Args:
            from_city: Город отправления
            to_city: Город прибытия
            
        Returns:
            Цена билета в рублях
        """
        pricing = self.get_pricing_matrix()
        route_key = f"{from_city}-{to_city}"
        
        # Пробуем найти прямое соответствие
        if route_key in pricing:
            return pricing[route_key]
        
        # Возвращаем базовую цену
        return pricing.get("default", 15.0)


# Singleton instance для использования во всем приложении
_config_loader_instance: RouteConfigLoader | None = None


def get_config_loader() -> RouteConfigLoader:
    """
    Возвращает singleton экземпляр загрузчика конфигурации.
    
    Returns:
        Экземпляр RouteConfigLoader
    """
    global _config_loader_instance
    if _config_loader_instance is None:
        _config_loader_instance = RouteConfigLoader()
    return _config_loader_instance


def reload_config() -> None:
    """Перезагружает конфигурацию (для тестирования или обновления данных)."""
    global _config_loader_instance
    _config_loader_instance = None
