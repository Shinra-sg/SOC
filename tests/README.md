# 🧪 Тесты проекта Atlas2

## Структура тестов

```
tests/
├── README.md                    # Этот файл
├── test_utils.py               # Тесты утилит (date, time, config)
├── test_tools.py               # Тесты инструментов бронирования
└── test_integration_simple.py  # Интеграционные тесты
```

---

## 🚀 Быстрый запуск всех тестов

```bash
# Из корневой директории проекта
cd /Users/shinra/prog/шлак/atlas2/crew-atl/crew_atl

# Запуск всех тестов по порядку
python3 tests/test_utils.py && \
python3 tests/test_tools.py && \
python3 tests/test_integration_simple.py
```

---

## 📋 Запуск отдельных тестов

### 1. Тесты утилит
```bash
python3 tests/test_utils.py
```

**Проверяет:**
- Нормализацию дат (различные форматы)
- Нормализацию времени (различные форматы)
- Загрузку конфигурации из YAML

**Ожидаемый результат:**
```
============================================================
Тестирование утилит проекта atlas2
============================================================
...
✓ Все тесты пройдены успешно!
```

---

### 2. Тесты инструментов
```bash
python3 tests/test_tools.py
```

**Проверяет:**
- RouteCheckerTool (проверка маршрутов)
- TimeCheckerTool (проверка времени)
- TicketPricingTool (расчет цен)

**Ожидаемый результат:**
```
============================================================
Тестирование инструментов бронирования
============================================================
...
✓ Все тесты инструментов пройдены успешно!
```

---

### 3. Интеграционные тесты
```bash
python3 tests/test_integration_simple.py
```

**Проверяет:**
- Переменные окружения
- Загрузку всех конфигураций
- Полный workflow бронирования
- Создание агентов с LLM

**Ожидаемый результат:**
```
======================================================================
ИНТЕГРАЦИОННЫЙ ТЕСТ ПРОЕКТА
======================================================================
...
✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!
```

---

## 🔍 Что тестируется

### Уровень 1: Утилиты (Unit tests)
- ✅ `date_utils.normalize_date_string()` - 4 формата дат
- ✅ `time_utils.normalize_time_string()` - 6 форматов времени
- ✅ `config_loader.get_config_loader()` - загрузка YAML

### Уровень 2: Инструменты (Component tests)
- ✅ RouteCheckerTool - 3 сценария (доступный, неизвестный, заблокированный)
- ✅ TimeCheckerTool - 5 сценариев (доступное, недоступное, форматы)
- ✅ TicketPricingTool - 2 сценария (известный маршрут, базовая цена)

### Уровень 3: Интеграция (Integration tests)
- ✅ Окружение (.env переменные)
- ✅ Конфигурация (города, маршруты, агенты)
- ✅ Workflow (маршрут → время → цена)
- ✅ Создание агентов с LLM

---

## ⚙️ Требования

### Обязательные:
- Python 3.10+
- Установленные зависимости: `crewai`, `pydantic`, `pyyaml`, `python-dotenv`
- Файл `.env` с переменными:
  ```
  MODEL=google/gemini-2.0-flash-lite
  GEMINI_API_KEY=your_api_key_here
  ```

### Проверка зависимостей:
```bash
pip3 list | grep -E "crewai|pydantic|PyYAML|dotenv"
```

---

## 🐛 Troubleshooting

### Проблема: `ModuleNotFoundError`
**Решение**: Убедись, что запускаешь из корневой директории проекта
```bash
cd /Users/shinra/prog/шлак/atlas2/crew-atl/crew_atl
```

### Проблема: `GEMINI_API_KEY не установлен`
**Решение**: Создай файл `.env` в корне проекта:
```bash
echo "MODEL=google/gemini-2.0-flash-lite" > .env
echo "GEMINI_API_KEY=your_key" >> .env
```

### Проблема: Тесты падают с ошибкой YAML
**Решение**: Проверь, что файл `src/crew_atl/config/agents.yaml` существует и валиден:
```bash
python3 -c "import yaml; yaml.safe_load(open('src/crew_atl/config/agents.yaml'))"
```

---

## 📊 Интерпретация результатов

### ✅ Все тесты пройдены
```
✓ Все тесты пройдены успешно!
Exit Code: 0
```
**Значение**: Проект готов к работе!

### ❌ Тест провален
```
✗ Ошибка при тестировании: ...
Exit Code: 1
```
**Действия**: Читай сообщение об ошибке, проверяй соответствующий компонент

---

## 🎯 Следующие шаги

После успешного прохождения тестов:

1. **Запусти простой тест бронирования**:
   ```bash
   python3 simple_test.py
   ```

2. **Запусти полный пример**:
   ```bash
   python3 example_usage.py
   ```

3. **Или запусти crew напрямую**:
   ```bash
   python3 -m src.crew_atl.main
   ```

---

## 📝 Добавление новых тестов

Чтобы добавить свой тест:

1. Создай файл `tests/test_your_feature.py`
2. Используй структуру:
```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def test_your_feature():
    # Твой тест здесь
    pass

if __name__ == "__main__":
    try:
        test_your_feature()
        print("✓ Тест пройден!")
    except Exception as e:
        print(f"✗ Тест провален: {e}")
        sys.exit(1)
```

---

*Документация обновлена: 16 августа 2026*
