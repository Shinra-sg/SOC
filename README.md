# 🔐 AI-SOC: Security Operations Center

**Интеллектуальная мультиагентная система детекции и реагирования на киберугрозы**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![CrewAI](https://img.shields.io/badge/CrewAI-0.201.1-green.svg)](https://github.com/joaomdmoura/crewAI)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

---

## 🎯 Описание проекта

AI-SOC — это автоматизированная система мониторинга информационной безопасности, построенная на базе мультиагентной архитектуры с использованием искусственного интеллекта.

### Основные возможности:

- 🔍 **Анализ логов** — автоматический парсинг и нормализация событий безопасности
- 🚨 **Детекция угроз** — выявление атак в реальном времени (brute-force, SQL injection, malware)
- 🛡️ **Сканирование уязвимостей** — поиск CVE и слабых мест в инфраструктуре
- ⚡ **Автоматическое реагирование** — блокировка атак, изоляция хостов
- 🌐 **Threat Intelligence** — обогащение данными о актуальных угрозах

---

## 🤖 Мультиагентная архитектура

Система состоит из **5 специализированных AI-агентов**:

### 1. **Log Analyzer Agent** 📊
Анализирует и нормализует события безопасности из различных источников (firewall, IDS, auth-логи).

### 2. **Threat Detector Agent** 🎯
Детектирует подозрительную активность, используя signature-based и anomaly-based методы.

### 3. **Vulnerability Scanner Agent** 🔍
Проактивно ищет уязвимости в инфраструктуре, проверяет наличие известных CVE.

### 4. **Incident Responder Agent** ⚡
Автоматически реагирует на инциденты: блокирует IP, изолирует хосты, создает тикеты.

### 5. **Threat Intelligence Agent** 🌐
Обогащает данные из threat feeds (VirusTotal, AbuseIPDB), отслеживает новые угрозы.

---

## 🏗️ Архитектура

```
┌─────────────────────────────────────────────────────┐
│                    AI-SOC System                     │
├─────────────────────────────────────────────────────┤
│                                                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐          │
│  │  Logs    │  │ Threat   │  │  Vuln    │          │
│  │ Analyzer │→ │ Detector │→ │ Scanner  │          │
│  └──────────┘  └──────────┘  └──────────┘          │
│                      ↓                               │
│              ┌──────────────┐                        │
│              │   Incident   │                        │
│              │  Responder   │                        │
│              └──────────────┘                        │
│                      ↑                               │
│              ┌──────────────┐                        │
│              │   Threat     │                        │
│              │ Intelligence │                        │
│              └──────────────┘                        │
│                                                       │
├─────────────────────────────────────────────────────┤
│              Database Layer (PostgreSQL)             │
│   Events | Threats | IoC | CVE | Incidents | Assets │
└─────────────────────────────────────────────────────┘
```

---

## 📦 Установка

### Требования:
- Python 3.10+
- PostgreSQL 14+ (или SQLite для разработки)
- Git

### Быстрый старт:

```bash
# Клонируем репозиторий
git clone <repository-url>
cd ai-soc

# Создаем виртуальное окружение
python3 -m venv venv
source venv/bin/activate  # для Linux/Mac
# или
venv\Scripts\activate  # для Windows

# Устанавливаем зависимости
pip install -e .

# Копируем и настраиваем .env
cp .env.example .env
# Отредактируйте .env и добавьте свои API ключи

# Инициализируем базу данных
python -m ai_soc.database.init_db

# Загружаем тестовые данные (опционально)
python -m ai_soc.database.load_samples
```

---

## 🚀 Использование

### Режим реального времени (мониторинг):
```bash
ai-soc --monitor
```

### Анализ архивных логов:
```bash
ai-soc --analyze --input logs/security.log
```

### Сканирование уязвимостей:
```bash
ai-soc --scan --target 192.168.1.0/24
```

### Генерация отчета:
```bash
ai-soc --report --format pdf --output report.pdf
```

---

## 🗄️ База данных

Система использует PostgreSQL для хранения:
- **security_events** — события безопасности
- **threats** — обнаруженные угрозы
- **indicators_of_compromise** — IoC (IP, domains, hashes)
- **vulnerabilities** — известные CVE
- **assets** — инфраструктура (серверы, устройства)
- **incidents** — инциденты безопасности
- **response_actions** — выполненные действия

Подробнее: [docs/DATABASE.md](docs/DATABASE.md)

---

## 🧪 Тестирование

```bash
# Запуск всех тестов
pytest tests/

# Только unit-тесты
pytest tests/unit/

# Интеграционные тесты
pytest tests/integration/

# Тесты сценариев атак
pytest tests/scenarios/

# С покрытием
pytest --cov=ai_soc tests/
```

---

## 📊 Примеры использования

### Сценарий 1: Обнаружение brute-force атаки

```python
from ai_soc import AISOC

# Инициализируем систему
soc = AISOC()

# Загружаем логи
events = soc.load_events(source="auth.log")

# Запускаем анализ
results = soc.analyze(events)

# Результат:
# ✓ Detected: Brute-force attack from 192.168.1.100
# ✓ Action: IP blocked in firewall
# ✓ Incident created: INC-2024-001
```

### Сценарий 2: Сканирование уязвимостей

```python
# Сканируем сеть
vulnerabilities = soc.scan_network("192.168.1.0/24")

# Результат:
# Found 3 critical vulnerabilities:
# - CVE-2021-44228 (Log4j RCE) on web-server-01
# - CVE-2022-XXXX (OpenSSL) on app-server-03
# ...
```

---

## 🛠️ Конфигурация

### config/security_data.yaml
Содержит:
- Attack patterns (брут-форс, SQL injection, XSS)
- Threat signatures
- Severity levels
- Response rules

### config/agents.yaml
Конфигурация агентов:
- Роли и цели
- Промпты
- Инструменты

Подробнее: [docs/CONFIGURATION.md](docs/CONFIGURATION.md)

---

## 📚 Документация

- [Архитектура системы](docs/ARCHITECTURE.md)
- [Описание агентов](docs/AGENTS.md)
- [Инструменты](docs/TOOLS.md)
- [База данных](docs/DATABASE.md)
- [Руководство пользователя](docs/USER_GUIDE.md)
- [API Reference](docs/API.md)

---

## 🎓 Дипломная работа

Этот проект разработан как дипломная работа по теме:
> "Интеллектуальная мультиагентная система детекции и реагирования на киберугрозы на основе анализа событий безопасности"

### Ключевые достижения:
- ✅ Мультиагентная архитектура на базе CrewAI
- ✅ Автоматическая детекция 10+ типов атак
- ✅ Интеграция с threat intelligence feeds
- ✅ Автоматическое реагирование на инциденты
- ✅ Покрытие тестами > 70%

---

## 🌍 Сферы применения

- 🏦 **Банки и финтех** — защита транзакций и данных клиентов
- 🛒 **E-commerce** — детекция fraud и защита от ботов
- 🏥 **Здравоохранение** — защита медицинских данных (HIPAA compliance)
- 🏢 **Enterprise** — корпоративная защита (100+ сотрудников)
- 🚀 **Стартапы** — SOC-as-a-Service модель

---

## 🔧 Технологический стек

- **AI/LLM**: Google Gemini, CrewAI
- **Backend**: Python 3.10+, SQLAlchemy
- **Database**: PostgreSQL / SQLite
- **Testing**: pytest, coverage
- **Documentation**: Markdown, Sphinx

---

## 📈 Roadmap

Полный план развития проекта: [ROADMAP.md](ROADMAP.md)

### Текущая версия: v0.1.0 (MVP)
- [x] Базовая архитектура
- [x] 5 агентов
- [x] 15 инструментов
- [x] База данных
- [ ] Web dashboard (в разработке)
- [ ] ML-модели для детекции (планируется)

---

## 🤝 Contributing

Проект создан в образовательных целях. Предложения и улучшения приветствуются!

---

## 📄 Лицензия

MIT License - см. [LICENSE](LICENSE)

---

## 👨‍💻 Автор

**Дипломный проект**  
Направление: Информационная безопасность  
Год: 2026

---

## 📞 Контакты

- Email: security@example.com
- GitHub: [github.com/yourusername/ai-soc](https://github.com)

---

*Защищаем цифровой мир с помощью искусственного интеллекта* 🔐🤖
