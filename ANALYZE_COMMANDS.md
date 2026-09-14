# Команды для анализа диалогов

## Ручной запуск анализа

### Анализ последних N диалогов
```bash
cd /Users/shinra/prog/atlas2/crew-atl/crew_atl
source /Users/shinra/prog/atlas2/crewai-env/bin/activate
python3 -m src.crew_atl.main analyze [N]
```

**Примеры:**
- `python3 -m src.crew_atl.main analyze` - анализ последних 20 диалогов (по умолчанию)
- `python3 -m src.crew_atl.main analyze 5` - анализ последних 5 диалогов
- `python3 -m src.crew_atl.main analyze 50` - анализ последних 50 диалогов

### Запуск тестов
```bash
python3 -m src.crew_atl.main batch [N]  # Запуск N тестов подряд
python3 -m src.crew_atl.main           # Запуск одного диалога
```

## Автоматический анализ

Система автоматически запускает анализ каждые 20 диалогов при выполнении тестов.

## Результаты анализа

Файлы анализа сохраняются в:
- `src/crew_atl/logs/analysis/batch_analysis_YYYYMMDD_HHMMSS.md`

Каждый файл содержит:
- Конкретные рекомендации по улучшению промптов
- Готовые блоки для вставки в конфигурацию
- Анализ проблем в диалогах
- Предложения по улучшению поведения агента

## Требования

- VPN должен быть включен для работы с LLM
- Переменная окружения `MODEL` должна быть установлена
- Рекомендуется установить `THROTTLE_SECONDS=8` для стабильности
