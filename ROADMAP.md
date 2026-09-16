# 🗺️ ROADMAP: AI-SOC Project Implementation

**Проект**: AI Security Operations Center (SOC)  
**Цель**: Интеллектуальная мультиагентная система детекции и реагирования на киберугрозы  
**Технологии**: CrewAI, Python, PostgreSQL, LLM (Gemini)

---

## 📋 Общая структура (8 фаз, 26 этапов)

**Общее время**: 66-95 часов  
**MVP время**: 25-30 часов

---

## 🎯 **PHASE 1: Подготовка и проектирование** (Foundation)

### **Этап 1.1: Переименование и реструктуризация проекта** ✅
**Цель**: Адаптировать существующую структуру под SOC-тематику

**Задачи**:
- [x] Переименовать проект: `crew-atl` → `ai-soc`
- [x] Обновить `pyproject.toml` (название, описание)
- [x] Обновить `README.md` под новую тематику
- [x] Создать `ARCHITECTURE.md` с описанием системы
- [x] Обновить `.gitignore` с правильными исключениями
- [x] Переименовать `src/crew_atl` → `src/ai_soc`
- [x] Обновить все импорты в Python файлах

**Результат**: ✅ Новая структура проекта с правильными названиями

**Время**: 30 минут → Завершено

---

### **Этап 1.2: Проектирование базы данных** ✅
**Цель**: Создать схему БД для security events

**Задачи**:
- [x] Создать SQL схему для PostgreSQL
- [x] Создать SQL схему для SQLite
- [x] Определить таблицы:
  - `security_events` (основные события)
  - `threats` (обнаруженные угрозы)
  - `indicators_of_compromise` (IoC)
  - `vulnerabilities` (CVE)
  - `assets` (инфраструктура)
  - `incidents` (инциденты)
  - `response_actions` (действия)
- [ ] Создать ER-диagramму
- [ ] Написать миграции (Alembic или plain SQL)

**Результат**: Файл `database/schema.sql` и диаграмма

**Время**: 1-2 часа

---

### **Этап 1.3: Подготовка тестовых данных** ✅
**Цель**: Создать realistic dataset для тестирования

**Задачи**:
- [x] Создать генератор синтетических логов
- [x] Подготовить sample security events (500 записей)
- [x] Создать список известных IoC (100 malicious IPs, domains)
- [x] Подготовить список CVE из известных уязвимостей (72 записи)
- [x] Создать mock assets (50 серверов, workstations)
- [x] Создать мастер-скрипт для генерации всех данных
- [x] Создать скрипт загрузки данных в БД

**Результат**: ✅ Файлы в `data/samples/`, все генераторы работают, данные загружены в БД

**Время**: 1-2 часа → Завершено

---

## 🔧 **PHASE 2: Core Infrastructure** (Backend)

### **Этап 2.1: Database Layer** ✅
**Цель**: Реализовать работу с БД

**Задачи**:
- [x] Создать `database/connection.py` (connection pool)
- [x] Создать `database/models.py` (ORM модели - SQLAlchemy)
- [x] Создать `database/repositories.py` (CRUD операции)
- [x] Написать тесты для DB layer
- [x] Создать документацию DATABASE_LAYER.md

**Результат**: ✅ Работающий DB layer с 7 ORM моделями, 7 repositories, connection pool

**Время**: 2-3 часа → Завершено

---

### **Этап 2.2: Configuration & Data Loading**
**Цель**: Загрузка конфигурации и данных

**Задачи**:
- [ ] Создать `config/security_data.yaml`:
  - Known attack patterns
  - Threat signatures
  - Severity levels
  - Response rules
- [ ] Обновить `utils/config_loader.py` под SOC
- [ ] Создать `utils/ioc_loader.py` (загрузка IoC)
- [ ] Создать `utils/cve_loader.py` (загрузка CVE)

**Результат**: Конфигурационные файлы и загрузчики

**Время**: 1-2 часа

---

## 🛠️ **PHASE 3: Tools Development** (Инструменты)

### **Этап 3.1: Log Analysis Tools**
**Цель**: Инструменты для анализа логов

**Задачи**:
- [ ] `LogParserTool` - парсинг различных форматов логов
- [ ] `LogNormalizerTool` - нормализация в единый формат
- [ ] `IPEnrichmentTool` - обогащение IP данными (geolocation, reputation)
- [ ] `EventCorrelationTool` - корреляция связанных событий

**Результат**: 4 инструмента в `tools/log_analysis.py`

**Время**: 3-4 часа

---

### **Этап 3.2: Threat Detection Tools**
**Цель**: Инструменты для детекции угроз

**Задачи**:
- [ ] `SignatureMatcherTool` - проверка по базе сигнатур
- [ ] `AnomalyDetectorTool` - детекция аномалий (simple ML)
- [ ] `BehaviorAnalyzerTool` - анализ поведения пользователей
- [ ] `ThreatScoringTool` - оценка severity угрозы (0-100)

**Результат**: 4 инструмента в `tools/threat_detection.py`

**Время**: 4-5 часов

---

### **Этап 3.3: Vulnerability Scanning Tools**
**Цель**: Инструменты для поиска уязвимостей

**Задачи**:
- [ ] `PortScannerTool` - сканирование портов (nmap-like)
- [ ] `CVECheckerTool` - проверка по базе CVE
- [ ] `ConfigAuditorTool` - аудит конфигураций
- [ ] `PatchStatusTool` - проверка обновлений

**Результат**: 4 инструмента в `tools/vulnerability_scanning.py`

**Время**: 3-4 часа

---

### **Этап 3.4: Incident Response Tools**
**Цель**: Инструменты для реагирования

**Задачи**:
- [ ] `FirewallControlTool` - блокировка IP (mock)
- [ ] `AccountManagementTool` - disable/enable accounts
- [ ] `HostIsolationTool` - изоляция хостов
- [ ] `TicketCreationTool` - создание incident tickets
- [ ] `EscalationTool` - эскалация к специалистам

**Результат**: 5 инструментов в `tools/incident_response.py`

**Время**: 3-4 часа

---

### **Этап 3.5: Threat Intelligence Tools**
**Цель**: Инструменты для threat intelligence

**Задачи**:
- [ ] `ThreatFeedParserTool` - парсинг threat feeds
- [ ] `IOCEnrichmentTool` - обогащение IoC данными
- [ ] `CVEMonitorTool` - мониторинг новых CVE
- [ ] `TTPAnalyzerTool` - MITRE ATT&CK mapping

**Результат**: 4 инструмента в `tools/threat_intelligence.py`

**Время**: 3-4 часа

---

## 🤖 **PHASE 4: Agents Development** (Агенты)

### **Этап 4.1: Log Analyzer Agent**
**Цель**: Агент для анализа логов

**Задачи**:
- [ ] Создать `agents/log_analyzer.py`
- [ ] Написать промпты в `config/agents.yaml`
- [ ] Подключить log analysis tools
- [ ] Написать тесты для агента

**Результат**: Работающий Log Analyzer Agent

**Время**: 2-3 часа

---

### **Этап 4.2: Threat Detector Agent**
**Цель**: Агент для детекции угроз

**Задачи**:
- [ ] Создать `agents/threat_detector.py`
- [ ] Написать промпты с правилами детекции
- [ ] Подключить threat detection tools
- [ ] Добавить ML-модели (опционально)
- [ ] Написать тесты

**Результат**: Работающий Threat Detector Agent

**Время**: 3-4 часа

---

### **Этап 4.3: Vulnerability Scanner Agent**
**Цель**: Агент для сканирования уязвимостей

**Задачи**:
- [ ] Создать `agents/vulnerability_scanner.py`
- [ ] Написать промпты с правилами сканирования
- [ ] Подключить vulnerability scanning tools
- [ ] Интеграция с CVE базой
- [ ] Написать тесты

**Результат**: Работающий Vulnerability Scanner Agent

**Время**: 2-3 часа

---

### **Этап 4.4: Incident Responder Agent**
**Цель**: Агент для реагирования на инциденты

**Задачи**:
- [ ] Создать `agents/incident_responder.py`
- [ ] Написать промпты с правилами реагирования
- [ ] Подключить incident response tools
- [ ] Создать систему уровней реагирования (L0, L1, L2)
- [ ] Написать тесты

**Результат**: Работающий Incident Responder Agent

**Время**: 3-4 часа

---

### **Этап 4.5: Threat Intelligence Agent**
**Цель**: Агент для threat intelligence

**Задачи**:
- [ ] Создать `agents/threat_intelligence.py`
- [ ] Написать промпты для анализа угроз
- [ ] Подключить threat intelligence tools
- [ ] Интеграция с external feeds (VirusTotal, AbuseIPDB)
- [ ] Написать тесты

**Результат**: Работающий Threat Intelligence Agent

**Время**: 2-3 часа

---

## 🔗 **PHASE 5: Integration & Orchestration**

### **Этап 5.1: Tasks Configuration**
**Цель**: Определить задачи для агентов

**Задачи**:
- [ ] Обновить `config/tasks.yaml`:
  - `log_analysis_task`
  - `threat_detection_task`
  - `vulnerability_scan_task`
  - `incident_response_task`
  - `threat_intelligence_task`
- [ ] Определить dependencies между задачами
- [ ] Определить output formats

**Результат**: Конфигурация задач в YAML

**Время**: 1-2 часа

---

### **Этап 5.2: Crew Orchestration**
**Цель**: Связать агентов в единую систему

**Задачи**:
- [ ] Обновить `crew.py` с новыми агентами
- [ ] Настроить Process (Sequential/Hierarchical)
- [ ] Определить workflow: logs → threats → response
- [ ] Добавить error handling между агентами
- [ ] Добавить logging всех взаимодействий

**Результат**: Работающая оркестрация агентов

**Время**: 2-3 часа

---

### **Этап 5.3: Main Application Logic**
**Цель**: Точка входа в систему

**Задачи**:
- [ ] Обновить `main.py`:
  - Загрузка логов из БД или файла
  - Запуск crew
  - Сохранение результатов
  - Генерация отчетов
- [ ] Добавить CLI interface (argparse)
- [ ] Добавить режимы работы:
  - `--realtime` - мониторинг в реальном времени
  - `--batch` - анализ архивных логов
  - `--scan` - сканирование уязвимостей

**Результат**: Полнофункциональный main.py

**Время**: 2-3 часа

---

## 🧪 **PHASE 6: Testing & Quality**

### **Этап 6.1: Unit Tests**
**Цель**: Тесты для всех компонентов

**Задачи**:
- [ ] Тесты для всех tools (20+ инструментов)
- [ ] Тесты для database layer
- [ ] Тесты для utils (config, loaders)
- [ ] Покрытие > 70%

**Результат**: Файлы в `tests/unit/`

**Время**: 4-5 часов

---

### **Этап 6.2: Integration Tests**
**Цель**: Тесты взаимодействия компонентов

**Задачи**:
- [ ] Тест полного workflow: logs → detection → response
- [ ] Тест взаимодействия агентов
- [ ] Тест с реальными sample данными
- [ ] Тест performance (обработка 1000 events)

**Результат**: Файлы в `tests/integration/`

**Время**: 3-4 часа

---

### **Этап 6.3: Scenario Tests**
**Цель**: Тесты реальных сценариев атак

**Задачи**:
- [ ] Сценарий 1: Brute-force атака
- [ ] Сценарий 2: SQL injection попытка
- [ ] Сценарий 3: Malware detection
- [ ] Сценарий 4: Аномальное поведение пользователя
- [ ] Сценарий 5: Обнаружение новой CVE

**Результат**: Файлы в `tests/scenarios/`

**Время**: 3-4 часа

---

## 📊 **PHASE 7: Visualization & Reporting**

### **Этап 7.1: Reports Generation**
**Цель**: Генерация отчетов

**Задачи**:
- [ ] Создать `reporting/report_generator.py`
- [ ] Security Summary Report (PDF/HTML)
- [ ] Incident Timeline Report
- [ ] Vulnerability Report (по CVE)
- [ ] Threat Intelligence Report
- [ ] Executive Summary для management

**Результат**: Модуль генерации отчетов

**Время**: 2-3 часа

---

### **Этап 7.2: Dashboard (Optional)**
**Цель**: Веб-интерфейс для SOC

**Задачи**:
- [ ] Простой Flask/FastAPI сервер
- [ ] Dashboard со статистикой:
  - Events per minute
  - Top threats
  - Recent incidents
  - Asset status
- [ ] Real-time updates (WebSockets опционально)

**Результат**: Web dashboard (опционально)

**Время**: 4-6 часов (если делать)

---

## 📚 **PHASE 8: Documentation & Finalization**

### **Этап 8.1: Technical Documentation**
**Цель**: Полная техническая документация

**Задачи**:
- [ ] `docs/INSTALLATION.md` - установка и настройка
- [ ] `docs/ARCHITECTURE.md` - архитектура системы
- [ ] `docs/AGENTS.md` - описание агентов
- [ ] `docs/TOOLS.md` - описание инструментов
- [ ] `docs/DATABASE.md` - схема БД
- [ ] `docs/API.md` - API reference (если есть)

**Результат**: Документация в `docs/`

**Время**: 3-4 часа

---

### **Этап 8.2: User Guide**
**Цель**: Руководство пользователя

**Задачи**:
- [ ] `docs/USER_GUIDE.md`:
  - Как запустить систему
  - Как загрузить логи
  - Как интерпретировать результаты
  - Troubleshooting
- [ ] Примеры использования
- [ ] FAQ

**Результат**: User Guide

**Время**: 2-3 часа

---

### **Этап 8.3: Diploma Materials**
**Цель**: Материалы для диплома

**Задачи**:
- [ ] Презентация (PowerPoint/Google Slides)
- [ ] Пояснительная записка (Word/LaTeX):
  - Введение
  - Обзор аналогов
  - Архитектура
  - Реализация
  - Тестирование
  - Заключение
- [ ] Видео-демонстрация (3-5 минут)
- [ ] Poster/инфографика

**Результат**: Материалы для защиты диплома

**Время**: 6-10 часов

---

## 📅 **Timeline & Estimates**

| Phase | Этапы | Примерное время |
|-------|-------|-----------------|
| **PHASE 1** | Подготовка (3 этапа) | 3-5 часов |
| **PHASE 2** | Infrastructure (2 этапа) | 3-5 часов |
| **PHASE 3** | Tools (5 этапов) | 16-21 час |
| **PHASE 4** | Agents (5 этапов) | 12-17 часов |
| **PHASE 5** | Integration (3 этапа) | 5-8 часов |
| **PHASE 6** | Testing (3 этапа) | 10-13 часов |
| **PHASE 7** | Visualization (2 этапа) | 6-9 часов |
| **PHASE 8** | Documentation (3 этапа) | 11-17 часов |
| **ИТОГО** | **26 этапов** | **66-95 часов** |

---

## 🎯 **MVP (Minimum Viable Product)**

Если нужно быстрее, можно сделать MVP:

### **MVP Scope** (25-30 часов):
1. ✅ Phase 1: Подготовка (базовая)
2. ✅ Phase 2: Database (SQLite)
3. ✅ Phase 3: 2 агента вместо 5:
   - Log Analyzer + Threat Detector
4. ✅ Phase 3: 10 инструментов вместо 20
5. ✅ Phase 5: Базовая оркестрация
6. ✅ Phase 6: Основные тесты
7. ✅ Phase 8: Минимальная документация

---

## 🚀 **Приоритизация**

### **Must Have** (для диплома):
- ✅ 5 агентов (можно упростить функционал)
- ✅ База данных (хотя бы SQLite)
- ✅ 10-15 инструментов
- ✅ Тесты (хотя бы основные)
- ✅ Документация
- ✅ 2-3 реальных сценария

### **Should Have**:
- Reports generation
- CLI interface
- Performance тесты

### **Nice to Have**:
- Web dashboard
- Real-time monitoring
- ML-модели для детекции

---

## 📊 **Прогресс**

```
PHASE 1: [▓▓▓] 3/3   (100%) - ЗАВЕРШЕНО ✅
  ✅ Этап 1.1: Переименование и реструктуризация
  ✅ Этап 1.2: Проектирование базы данных
  ✅ Этап 1.3: Подготовка тестовых данных

PHASE 2: [▓] 1/2   (50%) - В процессе
  ✅ Этап 2.1: Database Layer
  [ ] Этап 2.2: Tools Implementation
PHASE 4: [ ] 0/5   (0%)
PHASE 5: [ ] 0/3   (0%)
PHASE 6: [ ] 0/3   (0%)
PHASE 7: [ ] 0/2   (0%)
PHASE 8: [ ] 0/3   (0%)
────────────────────────
ИТОГО:   [▓▓] 4/26  (15%)
```

---

## 🎯 **Текущий этап**

**Завершено**: 
- ✅ PHASE 1 - Project Foundation (100%)
- ✅ PHASE 2.1 - Database Layer

**Следующий этап**: PHASE 2.2 - Tools Implementation

**Следующие шаги**:
1. Создать базовые tools для агентов
2. Log Analysis tools
3. Threat Detection tools
4. Vulnerability Scanning tools
5. Incident Response tools

---

## 📝 **Примечания**

- Этот roadmap — живой документ, будет обновляться по ходу работы
- Время — приблизительное, зависит от опыта и темпа
- Можно менять приоритеты в зависимости от требований диплома
- MVP можно защитить как диплом, Full version — как коммерческий продукт

---

*Roadmap создан: 16 августа 2026*  
*Последнее обновление: 16 августа 2026*
