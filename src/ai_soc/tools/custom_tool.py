"""
Инструменты для работы с маршрутами, бронированием и взаимодействием с пользователем.
"""

from crewai.tools import BaseTool
from typing import Type, List, Dict, Optional, Tuple
from pydantic import BaseModel, Field
import json
import os
import yaml
import random
from crewai.llm import LLM

from ..utils.config_loader import get_config_loader
from ..utils.date_utils import normalize_date_string, get_next_available_date
from ..utils.time_utils import normalize_time_string, find_closest_time


# Инициализируем загрузчик конфигурации
config = get_config_loader()

# Загружаем данные из конфигурации
VALID_CITIES = config.get_valid_cities()
BLOCKED_CITIES = config.get_blocked_cities()
ROUTES = config.get_routes()
ROUTE_TIMES = config.get_route_times()
BLACKOUT_DATES = config.get_blackout_dates()


# ============================================================================
# Pydantic модели для валидации входных данных
# ============================================================================

class CheckRouteInput(BaseModel):
    """Модель для проверки доступности маршрута."""
    departure_city: str = Field(..., description="Город отправления")
    arrival_city: str = Field(..., description="Город прибытия")
    date: str = Field(..., description="Дата поездки в формате YYYY-MM-DD")


class CheckTimeInput(BaseModel):
    """Модель для проверки доступности времени отправления."""
    departure_city: str = Field(..., description="Город отправления")
    arrival_city: str = Field(..., description="Город прибытия")
    date: str = Field(..., description="Дата поездки")
    desired_time: str = Field(..., description="Желаемое время в формате HH:MM")


class GetTicketsInput(BaseModel):
    """Модель для получения информации о билетах и ценах."""
    departure_city: str = Field(..., description="Город отправления")
    arrival_city: str = Field(..., description="Город прибытия")
    date: str = Field(..., description="Дата поездки")
    time: str = Field(..., description="Время отправления")
    passengers: int = Field(..., description="Количество пассажиров", ge=1, le=50)


class AskUserInput(BaseModel):
    """Модель для вопроса пользователю."""
    question: str = Field(..., description="Вопрос пользователю")
    hint: Optional[str] = Field(None, description="Подсказка по формату ответа")


class UpdateAgentPromptInput(BaseModel):
    """Модель для обновления промпта агента."""
    agent_name: str = Field(..., description="Имя агента, чей промпт нужно обновить")
    field_to_update: str = Field(
        ..., 
        description="Поле промпта для обновления (role, goal, backstory)"
    )
    new_content: str = Field(..., description="Новое содержимое для поля промпта")


class UserResponseInput(BaseModel):
    """Модель для генерации ответа пользователя."""
    bot_question: str = Field(..., description="Вопрос от бота, на который нужно ответить")


class LLMUserResponseInput(BaseModel):
    """Модель для генерации ответа пользователя с помощью LLM."""
    bot_question: str = Field(..., description="Вопрос от бота, на который нужно ответить")
    context: Optional[str] = Field(None, description="Необязательный контекст диалога")


class StressTestScenarioInput(BaseModel):
    """Модель для генерации стресс-тестовых сценариев."""
    bot_question: str = Field(..., description="Вопрос от бота, на который нужно ответить")
    context: Optional[str] = Field(None, description="Необязательный контекст диалога")


# ============================================================================
# Инструменты для работы с маршрутами и бронированием
# ============================================================================


class RouteCheckerTool(BaseTool):
    """Инструмент для проверки доступности маршрута между городами."""
    
    name: str = "Проверка маршрута"
    description: str = "Проверяет доступность маршрута между городами на указанную дату"
    args_schema: Type[BaseModel] = CheckRouteInput

    def _run(self, departure_city: str, arrival_city: str, date: str) -> str:
        """
        Проверяет доступность маршрута.
        
        Args:
            departure_city: Город отправления
            arrival_city: Город прибытия
            date: Дата поездки
            
        Returns:
            JSON с результатом проверки
        """
        hints: Dict[str, object] = {
            "valid_cities": VALID_CITIES, 
            "blocked_cities": list(BLOCKED_CITIES)
        }
        date_iso = normalize_date_string(date)
        
        # Проверка заблокированных городов
        if departure_city in BLOCKED_CITIES or arrival_city in BLOCKED_CITIES:
            return json.dumps({
                "available": False,
                "reason": "blocked_city",
                "message": f"Бронирование в {', '.join(BLOCKED_CITIES)} недоступно",
                "hints": hints
            }, ensure_ascii=False)
        
        # Проверка существования городов
        if departure_city not in VALID_CITIES or arrival_city not in VALID_CITIES:
            return json.dumps({
                "available": False,
                "reason": "unknown_city",
                "message": "Неизвестный город отправления или прибытия",
                "hints": hints
            }, ensure_ascii=False)

        # Проверка существования маршрута
        route_key = (departure_city, arrival_city)
        if route_key not in ROUTES:
            # Предлагаем альтернативы
            alternatives = [
                {"arrival_city": b, "times": ROUTE_TIMES.get((departure_city, b), [])}
                for (a, b) in ROUTES if a == departure_city
            ]
            return json.dumps({
                "available": False,
                "reason": "route_unavailable",
                "message": f"Маршрут {departure_city} → {arrival_city} недоступен на {date_iso}",
                "alternatives": alternatives,
                "hints": hints
            }, ensure_ascii=False)

        # Проверка blackout дат
        if date_iso in BLACKOUT_DATES:
            next_date = get_next_available_date(date_iso, BLACKOUT_DATES)
            return json.dumps({
                "available": False,
                "reason": "date_blackout",
                "message": f"На дату {date_iso} рейсы недоступны",
                "suggested_date": next_date,
                "times": ROUTE_TIMES.get(route_key, []),
                "hints": hints
            }, ensure_ascii=False)

        # Маршрут доступен
        return json.dumps({
            "available": True,
            "message": f"Маршрут {departure_city} → {arrival_city} доступен на {date_iso}",
            "times": ROUTE_TIMES.get(route_key, []),
            "hints": hints
        }, ensure_ascii=False)


class TimeCheckerTool(BaseTool):
    """Инструмент для проверки доступности времени отправления."""
    
    name: str = "Проверка времени"
    description: str = "Проверяет доступность времени отправления и предлагает ближайшее доступное"
    args_schema: Type[BaseModel] = CheckTimeInput

    def _run(self, departure_city: str, arrival_city: str, date: str, desired_time: str) -> str:
        """
        Проверяет доступность времени отправления.
        
        Args:
            departure_city: Город отправления
            arrival_city: Город прибытия
            date: Дата поездки
            desired_time: Желаемое время в различных форматах
            
        Returns:
            JSON с результатом проверки времени
        """
        # Нормализуем время
        normalized_time = normalize_time_string(desired_time)
        
        # Получаем доступные времена для маршрута
        route_key = (departure_city, arrival_city)
        route_times = ROUTE_TIMES.get(route_key, [])
        
        if not route_times:
            return json.dumps({
                "available": False,
                "reason": "route_no_times",
                "message": "Для маршрута нет доступного расписания",
                "suggested_times": [],
            }, ensure_ascii=False)

        # Проверяем точное совпадение
        if normalized_time in route_times:
            return json.dumps({
                "available": True,
                "time": normalized_time,
                "message": f"Время {normalized_time} доступно"
            }, ensure_ascii=False)

        # Ищем ближайшее время
        closest_time = find_closest_time(normalized_time or "00:00", route_times)
        
        return json.dumps({
            "available": False,
            "suggested_time": closest_time,
            "suggested_times": route_times,
            "message": f"Время {desired_time} недоступно. Ближайшее доступное: {closest_time}"
        }, ensure_ascii=False)


class TicketPricingTool(BaseTool):
    """Инструмент для получения информации о ценах на билеты."""
    
    name: str = "Получение цен на билеты"
    description: str = "Получает информацию о тарифах и стоимости билетов"
    args_schema: Type[BaseModel] = GetTicketsInput

    def _run(self, departure_city: str, arrival_city: str, date: str, time: str, passengers: int) -> str:
        """
        Рассчитывает стоимость билетов.
        
        нужно будет переделать архитектуру глобального кластера
        под полноценный докер компоуз
        учитывая что зависимости до сих по не расставлены

        а так же

        необходимо настроить правильное подключение библиотек совместимых с гугл образ обработкой
        настроить автоматическое подключение впн
        для компилирования без ручной настройки из-за недоступности сервера в РБ
        так же обсудить юридические вопросы
        по поводу коректной работы с иностранными серверами


        Args:
            departure_city: Город отправления
            arrival_city: Город прибытия
            date: Дата поездки
            time: Время отправления
            passengers: Количество пассажиров
            
        Returns:
            JSON с информацией о ценах
        """
        base_price = config.get_base_price(departure_city, arrival_city)
        child_price = round(base_price / 2, 2)

        return json.dumps({
            "adult_price": base_price,
            "child_price": child_price,
            "total_adults": passengers,
            "total_children": 0,
            "total_cost": base_price * passengers,
            "message": f"Взрослый билет: {base_price} руб., Детский: {child_price} руб."
        }, ensure_ascii=False)



# ============================================================================
# Инструменты для взаимодействия с пользователем
# ============================================================================

class AskUserTool(BaseTool):
    """Инструмент для интерактивного взаимодействия с пользователем."""
    
    name: str = "Вопрос пользователю"
    description: str = "Задает вопрос пользователю и возвращает его ответ"
    args_schema: Type[BaseModel] = AskUserInput

    def _run(self, question: str, hint: Optional[str] = None) -> str:
        """
        Задает вопрос пользователю через консоль.
        
        Args:
            question: Текст вопроса
            hint: Необязательная подсказка по формату ответа
            
        Returns:
            Ответ пользователя
        """
        prompt = f"\n👤 Вопрос пользователю:\n{question}\n"
        if hint:
            prompt += f"(подсказка: {hint})\n"
        try:
            answer = input(prompt).strip()
        except (EOFError, KeyboardInterrupt):
            answer = ""
        return answer


class AutoAskUserTool(BaseTool):
    """Инструмент для автоматической генерации ответов пользователя (для тестирования)."""
    
    name: str = "Вопрос пользователю (авто)"
    description: str = "Задает вопрос пользователю и автоматически генерирует ответ на основе контекста"
    args_schema: Type[BaseModel] = AskUserInput

    def _run(self, question: str, hint: Optional[str] = None) -> str:
        """
        Генерирует автоматический ответ на основе типа вопроса.
        
        Args:
            question: Текст вопроса
            hint: Необязательная подсказка (не используется)
            
        Returns:
            Автоматически сгенерированный ответ
        """
        question_lower = question.lower()
        
        # Определяем тип вопроса и возвращаем соответствующий ответ
        if "город отправления" in question_lower or "откуда" in question_lower:
            return "Минск"
        elif "город прибытия" in question_lower or "куда" in question_lower:
            return "Гродно"
        elif "дата" in question_lower or "когда" in question_lower:
            return "2025-10-15"
        elif "время" in question_lower:
            return "11:00"
        elif "количество" in question_lower or "сколько" in question_lower:
            return "1"
        elif "взрослый" in question_lower or "детский" in question_lower:
            return "взрослый"
        elif "подтверждаете" in question_lower or "верно" in question_lower:
            return "да"
        elif "обратный" in question_lower:
            return "нет"
        else:
            return "да"


class UpdateAgentPromptInput(BaseModel):
    agent_name: str = Field(..., description="Имя агента, чей промпт нужно обновить")
    field_to_update: str = Field(..., description="Поле промпта для обновления (например, 'role', 'goal', 'backstory')")
    new_content: str = Field(..., description="Новое содержимое для поля промпта")


class UpdateAgentPromptTool(BaseTool):
    name: str = "Обновление промпта агента"
    description: str = "Обновляет поле (role, goal, backstory) промпта указанного агента в файле agents.yaml"
    args_schema: Type[BaseModel] = UpdateAgentPromptInput

    def _run(self, agent_name: str, field_to_update: str, new_content: str) -> str:
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'agents.yaml')
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f) or {}

            agent_aliases = {
                "агент бронирования": "booking_agent",
                "агент бронирования билетов на маршрутки": "booking_agent",
                "бот": "booking_agent",
                "booking_agent": "booking_agent",
                "аналитик диалогов": "dialogue_analyzer",
                "dialogue_analyzer": "dialogue_analyzer",
            }
            field_aliases = {
                "роль": "role",
                "role": "role",
                "цель": "goal",
                "goal": "goal",
                "предыстория": "backstory",
                "backstory": "backstory",
            }

            requested_name = (agent_name or "").strip()
            requested_field = (field_to_update or "").strip()

            resolved_agent_key = requested_name
            if resolved_agent_key not in config:
                key_candidate = agent_aliases.get(requested_name.lower())
                if key_candidate and key_candidate in config:
                    resolved_agent_key = key_candidate
                else:
                    matches = []
                    for k, v in config.items():
                        role_text = (v.get("role", "") or "").lower()
                        if requested_name.lower() and requested_name.lower() in role_text:
                            matches.append(k)
                    if len(matches) == 1:
                        resolved_agent_key = matches[0]
                    else:
                        available = ", ".join(config.keys())
                        return (
                            f"Ошибка: агент '{requested_name}' не найден. Доступные ключи: {available}. "
                            f"Попробуйте: 'booking_agent' или 'dialogue_analyzer'."
                        )

            resolved_field = field_aliases.get(requested_field.lower(), requested_field)
            if resolved_field not in {"role", "goal", "backstory"}:
                return (
                    f"Ошибка: поле '{requested_field}' не поддерживается. Используйте role | goal | backstory."
                )

            current_content = config[resolved_agent_key].get(resolved_field, "")
            config[resolved_agent_key][resolved_field] = f"{current_content}\n{new_content}".strip()
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.safe_dump(config, f, allow_unicode=True, sort_keys=False)
            return (
                f"Промпт агента '{resolved_agent_key}' поле '{resolved_field}' успешно обновлено."
            )
        except Exception as e:
            return f"Ошибка при обновлении промпта агента: {e}"


class UserResponseInput(BaseModel):
    bot_question: str = Field(..., description="Вопрос от бота, на который нужно ответить")


class UserResponseTool(BaseTool):
    name: str = "Ответ пользователя"
    description: str = "Генерирует ответ пользователя на основе вопроса бота и примеров диалогов"
    args_schema: Type[BaseModel] = UserResponseInput
    
    def _run(self, bot_question: str) -> str:
        question_lower = bot_question.lower()
        
        if "город отправления" in question_lower or "откуда" in question_lower:
            return "Минск"
        elif "город прибытия" in question_lower or "куда" in question_lower:
            return "Гродно"
        elif "дата" in question_lower or "когда" in question_lower:
            return "2025-10-15"
        elif "время" in question_lower:
            return "11:00"
        elif "количество" in question_lower or "сколько" in question_lower:
            return "1"
        elif "взрослый" in question_lower or "детский" in question_lower:
            return "взрослый"
        elif "подтверждаете" in question_lower or "верно" in question_lower:
            return "да"
        elif "обратный" in question_lower:
            return "нет"
        else:
            return "да"


class LLMUserResponseInput(BaseModel):
    bot_question: str = Field(..., description="Вопрос от бота, на который нужно ответить")
    context: Optional[str] = Field(None, description="Необязательный контекст диалога")


class LLMUserResponseTool(BaseTool):
    name: str = "ИИ-ответ пользователя"
    description: str = (
        "Генерирует ответ пользователя при помощи LLM на основе вопроса бота и контекста"
    )
    args_schema: Type[BaseModel] = LLMUserResponseInput

    def _run(self, bot_question: str, context: Optional[str] = None) -> str:
        model_name = os.getenv("MODEL") or "gemini/gemini-2.0-flash"
        api_key = os.getenv("GEMINI_API_KEY")
        llm = LLM(model=model_name, provider="google", api_key=api_key, temperature=0.2)

        q = (bot_question or "").lower()
        allowed_cities_hint = ", ".join([c for c in VALID_CITIES])

        qtype = "generic"
        format_hint = "Коротко."
        examples = ""
        if any(k in q for k in ["город отправ", "откуда", "город выезда", "пункт отправ"]):
            qtype = "departure_city"
            format_hint = "Ответь НАЗВАНИЕМ ОДНОГО города из списка."
            examples = f"Доступные города: {allowed_cities_hint}"
        elif any(k in q for k in ["город прибыт", "куда", "пункт назнач", "город назначения"]):
            qtype = "arrival_city"
            format_hint = "Ответь НАЗВАНИЕМ ОДНОГО города из списка."
            examples = f"Доступные города: {allowed_cities_hint}"
        elif any(k in q for k in ["дата", "какого числа", "на какое число", "когда"]):
            qtype = "date"
            format_hint = "Ответь в формате YYYY-MM-DD."
            examples = "Например: 2025-09-17"
        elif any(k in q for k in ["время", "во сколько", "желаемое время"]):
            qtype = "time"
            format_hint = "Ответь в формате HH:MM (24 часа)."
            examples = "Например: 11:00"
        elif any(k in q for k in ["сколько", "количество", "сколько билетов", "сколько мест"]):
            qtype = "passengers"
            format_hint = "Ответь ЧИСЛОМ (например: 1)."
            examples = ""
        elif any(k in q for k in ["тариф", "взрослый", "детский", "тип билета"]):
            qtype = "ticket_type"
            format_hint = "Ответь одним словом: 'взрослый' или 'детский'."
            examples = "Например: взрослый"
        elif any(k in q for k in ["подтверждаете", "всё верно", "оформить", "оформляем"]):
            qtype = "confirm"
            format_hint = "Ответь 'да' или 'нет'."
            examples = ""
        elif any(k in q for k in ["обратный", "обратный билет", "туда-обратно"]):
            qtype = "return"
            format_hint = "Ответь 'да' или 'нет'."
            examples = ""

        system_prompt = (
            "Ты выступаешь в роли пользователя и отвечаешь строго и кратко на КОНКРЕТНЫЙ вопрос бота бронирования. "
            "Отвечай только тем фрагментом, который просит вопрос, без пояснений и добавок. "
            "Формат для этого вопроса: " + format_hint + " " + examples + " "
            "СТРОГОЕ ПРАВИЛО: Никогда не отвечай городом 'Москва' или его вариациями (в т.ч. латиницей)."
        )
        user_prompt = (
            f"Тип вопроса: {qtype}\n"
            f"Вопрос бота: {bot_question}\n"
            f"Контекст: {context or '-'}\n"
            f"Ответ пользователя:"
        )

        try:
            response = llm.call(system_prompt=system_prompt, prompt=user_prompt)
            text = (response or "").strip()
            return text if text else "да"
        except Exception:
            return "да"


class StressTestScenarioInput(BaseModel):
    bot_question: str = Field(..., description="Вопрос от бота, на который нужно ответить")
    context: Optional[str] = Field(None, description="Необязательный контекст диалога")


class StressTestScenarioTool(BaseTool):
    name: str = "Стресс-тест сценарий"
    description: str = "Генерирует стрессовые сценарии для тестирования агента бронирования"
    args_schema: Type[BaseModel] = StressTestScenarioInput

    def _run(self, bot_question: str, context: Optional[str] = None) -> str:
        try:
            question_lower = bot_question.lower()
            
            import random
            scenario_type = random.choice([
                "confused_user",      # Путающийся пользователь
                "impatient_user",     # Нетерпеливый пользователь  
                "incomplete_info",    # Неполная информация
                "wrong_format",       # Неправильный формат
                "multiple_requests",   # Множественные запросы
                "contradictory_info", # Противоречивая информация
                "off_topic",         # Не по теме
                "aggressive_user"     # Агрессивный пользователь
            ])
            
            if any(word in question_lower for word in ["город", "откуда", "куда", "отправления", "прибытия"]):
                if scenario_type == "confused_user":
                    return random.choice([
                        "Э-э, Лида, э-э, Минск, Лида",  # Реальный пример путаницы
                        "А что ближе к аэропорту?",  # Реальный пример
                        "Я не знаю, которая станция ближе к аэропорту",  # Реальный пример
                        "Эм... а где это?",
                        "Не знаю, может Минск?"
                    ])
                elif scenario_type == "wrong_format":
                    return random.choice([
                        "Минск-Гродно",  # Реальный пример неправильного формата
                        "Минск, потом Гродно",  # Реальный пример
                        "Из Минска в Гродно",  # Слишком длинно
                        "Город Мосты"  # Реальный пример
                    ])
                elif scenario_type == "multiple_requests":
                    return random.choice([
                        "Минск в Гродно, а еще можно в Витебск, и в Гомель тоже",  # Реальный пример
                        "Э-э, Лида, э-э, Минск, Лида"  # Реальный пример
                    ])
                elif scenario_type == "off_topic":
                    return random.choice([
                        "А что ближе к аэропорту?",  # Реальный пример
                        "А есть ли туалет в автобусе?",  # Реальный пример
                        "А сколько стоит проезд в автобусе?",  # Реальный пример
                        "Это у меня сестра прилетает в 8 часов в аэропорте"  # Реальный пример
                    ])
                else:
                    return random.choice(VALID_CITIES)
                    
            elif any(word in question_lower for word in ["дата", "число", "день", "месяц"]):
                if scenario_type == "confused_user":
                    return random.choice([
                        "17 число",  # Реальный пример
                        "Не помню точно...",
                        "Может завтра?",
                        "Эм... скоро"
                    ])
                elif scenario_type == "wrong_format":
                    return random.choice([
                        "17 число",  # Реальный пример неполной даты
                        "18 число",  # Реальный пример
                        "15.09.24",  # Реальный пример неправильного формата
                        "15 сентября",  # Без года
                        "завтра"       # Относительная дата
                    ])
                elif scenario_type == "contradictory_info":
                    return random.choice([
                        "17 число 17",  # Реальный пример противоречия
                        "На шестнадцатое. Шестнадцатое ноль девятое. На сегодня",  # Реальный пример
                        "15 сентября, нет 16, нет 17... точно 15"
                    ])
                else:
                    return "15-09-2024"
                    
            elif any(word in question_lower for word in ["время", "час", "минут", "отправления"]):
                if scenario_type == "impatient_user":
                    return random.choice([
                        "Быстрее!",
                        "Сколько можно ждать?",
                        "Да любое время!",
                        "Хватит вопросов!"
                    ])
                elif scenario_type == "wrong_format":
                    return random.choice([
                        "На 6 часов утра",  # Реальный пример неправильного формата
                        "17 сентября 6:00 утра",  # Реальный пример смешивания даты и времени
                        "20:50",  # Реальный пример без даты
                        "12:50",  # Реальный пример неправильного времени
                        "6 утра",       # Без минут
                        "14-30",        # Неправильный разделитель
                        "после обеда"   # Относительное время
                    ])
                elif scenario_type == "incomplete_info":
                    return random.choice([
                        "6",            # Только час
                        "утром",        # Без конкретного времени
                        "после работы"  # Неопределенно
                    ])
                else:
                    return "14:30"
                    
            elif any(word in question_lower for word in ["сколько", "количество", "билет", "пассажир"]):
                if scenario_type == "confused_user":
                    return random.choice([
                        "А сколько нужно?",
                        "Не знаю...",
                        "Может один?",
                        "А сколько мест в автобусе?"
                    ])
                elif scenario_type == "wrong_format":
                    return random.choice([
                        "Один на маршрутку",  # Реальный пример избыточной информации
                        "один",         # Словами
                        "1 билет",      # С лишними словами
                        "1 место"       # Неправильная терминология
                    ])
                elif scenario_type == "contradictory_info":
                    return random.choice([
                        "Один, один",  # Реальный пример повторения
                        "Один, нет два, нет один точно"
                    ])
                elif scenario_type == "aggressive_user":
                    return "Да боже, сколько раз можно повторять? Один билет"  # Реальный пример агрессии
                else:
                    return "1"
                    
            elif any(word in question_lower for word in ["тариф", "взрослый", "детский", "стоимость"]):
                if scenario_type == "confused_user":
                    return random.choice([
                        "А какой дешевле?",
                        "Не знаю разницы",
                        "Что посоветуете?",
                        "А есть льготы?"
                    ])
                elif scenario_type == "wrong_format":
                    return random.choice([
                        "взрослый билет",  # С лишними словами
                        "обычный",         # Неправильная терминология
                        "полный"           # Неправильная терминология
                    ])
                else:
                    return "Взрослый"
                    
            elif any(word in question_lower for word in ["верно", "правильно", "подтверждаете", "согласны"]):
                if scenario_type == "aggressive_user":
                    return random.choice([
                        "Да блин, сколько раз повторять!",  # Реальный пример агрессии
                        "Конечно верно!",
                        "Хватит уже!"
                    ])
                elif scenario_type == "confused_user":
                    return random.choice([
                        "Всё уже забронировано",  # Реальный пример непонимания контекста
                        "Кому, куда запрос свой повторить?",  # Реальный пример
                        "А что если нет?",
                        "Не знаю..."
                    ])
                elif scenario_type == "contradictory_info":
                    return random.choice([
                        "Да, да, да, да",  # Реальный пример избыточного подтверждения
                        "Да, нет... да, точно да"
                    ])
                else:
                    return "Да"
                    
            else:
                # Общие стрессовые ответы
                if scenario_type == "off_topic":
                    return random.choice([
                        "А есть ли скидки?",  # Реальный пример
                        "А есть ли туалет в автобусе?",  # Реальный пример
                        "А можно ли отменить билет?",
                        "А можно ли с багажом?",
                        "Там 5 плюс"  # Реальный пример непонятной информации
                    ])
                elif scenario_type == "aggressive_user":
                    return random.choice([
                        "Да хватит уже!",
                        "Быстрее оформляйте!",
                        "Сколько можно ждать?",
                        "Я тороплюсь!"
                    ])
                elif scenario_type == "impatient_user":
                    return random.choice([
                        "Быстрее!",
                        "Скоро будет?",
                        "Давайте уже",
                        "Тороплюсь"
                    ])
                else:
                    return "Понятно"
                    
        except Exception as e:
            print(f"Ошибка генерации стрессового сценария: {e}")
            return "Минск"
