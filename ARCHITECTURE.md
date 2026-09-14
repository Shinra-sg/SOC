# 🏗️ AI-SOC: Архитектура системы

**Документ**: Техническая архитектура  
**Версия**: 1.0  
**Дата**: 16 августа 2026

---

## 📋 Содержание

1. [Обзор системы](#обзор-системы)
2. [Архитектурные принципы](#архитектурные-принципы)
3. [Компоненты системы](#компоненты-системы)
4. [Мультиагентная архитектура](#мультиагентная-архитектура)
5. [База данных](#база-данных)
6. [Workflow и процессы](#workflow-и-процессы)
7. [Интеграции](#интеграции)
8. [Масштабируемость](#масштабируемость)

---

## 🎯 Обзор системы

AI-SOC — это автоматизированный Security Operations Center, построенный на принципах мультиагентной архитектуры с использованием искусственного интеллекта.

### Ключевые характеристики:

- **Мультиагентная система**: 5 специализированных AI-агентов
- **Real-time мониторинг**: Обработка событий в реальном времени
- **Автоматическое реагирование**: Минимизация MTTR (Mean Time To Respond)
- **Интеллектуальная детекция**: AI + ML + Rule-based подходы
- **Расширяемость**: Модульная архитектура

---

## 🧭 Архитектурные принципы

### 1. **Separation of Concerns**
Каждый агент отвечает за свою специализированную задачу:
- Log Analyzer — только анализ логов
- Threat Detector — только детекция угроз
- и т.д.

### 2. **Modularity**
Инструменты и агенты — независимые модули, которые можно:
- Заменять
- Обновлять
- Добавлять новые

### 3. **Data-Driven**
Все решения основаны на данных:
- События из БД
- Конфигурация из YAML
- Threat intelligence feeds

### 4. **Fail-Safe**
Система продолжает работать при падении отдельных компонентов:
- Retry механизмы
- Fallback модели
- Graceful degradation

### 5. **Observability**
Полная прозрачность работы системы:
- Логирование всех действий
- Метрики производительности
- Audit trail

---

## 🧩 Компоненты системы

```
┌─────────────────────────────────────────────────────────────┐
│                      AI-SOC System                           │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────────┐         ┌─────────────────┐            │
│  │  Presentation   │         │   CLI / Web     │            │
│  │     Layer       │◄───────►│    Dashboard    │            │
│  └─────────────────┘         └─────────────────┘            │
│           │                                                   │
│  ┌────────▼────────────────────────────────────────┐        │
│  │          Application Layer (Orchestration)       │        │
│  │  ┌──────────────────────────────────────────┐   │        │
│  │  │         CrewAI Orchestrator              │   │        │
│  │  │  (crew.py - координация агентов)         │   │        │
│  │  └──────────────────────────────────────────┘   │        │
│  └──────────────────────────────────────────────────┘       │
│           │                                                   │
│  ┌────────▼────────────────────────────────────────┐        │
│  │           Agent Layer (AI Agents)                │        │
│  │  ┌────────┐ ┌────────┐ ┌────────┐ ┌─────────┐  │        │
│  │  │  Log   │ │ Threat │ │  Vuln  │ │Incident │  │        │
│  │  │Analyzer│ │Detector│ │Scanner │ │Responder│  │        │
│  │  └────────┘ └────────┘ └────────┘ └─────────┘  │        │
│  │                ┌─────────────┐                   │        │
│  │                │   Threat    │                   │        │
│  │                │Intelligence │                   │        │
│  │                └─────────────┘                   │        │
│  └──────────────────────────────────────────────────┘       │
│           │                                                   │
│  ┌────────▼────────────────────────────────────────┐        │
│  │           Tools Layer (Instruments)              │        │
│  │  ┌────────────────────────────────────────┐     │        │
│  │  │  20+ Specialized Tools:                │     │        │
│  │  │  - LogParserTool                       │     │        │
│  │  │  - SignatureMatcherTool                │     │        │
│  │  │  - CVECheckerTool                      │     │        │
│  │  │  - FirewallControlTool                 │     │        │
│  │  │  - ThreatFeedParserTool ... etc        │     │        │
│  │  └────────────────────────────────────────┘     │        │
│  └──────────────────────────────────────────────────┘       │
│           │                                                   │
│  ┌────────▼────────────────────────────────────────┐        │
│  │        Data Layer (Persistence)                  │        │
│  │  ┌────────────────────────────────────────┐     │        │
│  │  │    PostgreSQL / SQLite Database        │     │        │
│  │  │  Events | Threats | IoC | CVE | etc    │     │        │
│  │  └────────────────────────────────────────┘     │        │
│  └──────────────────────────────────────────────────┘       │
│           │                                                   │
│  ┌────────▼────────────────────────────────────────┐        │
│  │       External Integrations                      │        │
│  │  ┌───────┐ ┌───────┐ ┌─────┐ ┌─────────┐       │        │
│  │  │Virus  │ │Abuse  │ │ NVD │ │MITRE    │       │        │
│  │  │Total  │ │ IPDB  │ │ CVE │ │ATT&CK   │       │        │
│  │  └───────┘ └───────┘ └─────┘ └─────────┘       │        │
│  └──────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────┘
```

---

## 🤖 Мультиагентная архитектура

### Принцип работы CrewAI:

```python
# 1. Определяем агентов
log_analyzer = Agent(role="Log Analyzer", tools=[...])
threat_detector = Agent(role="Threat Detector", tools=[...])
...

# 2. Определяем задачи
task1 = Task(description="Analyze logs", agent=log_analyzer)
task2 = Task(description="Detect threats", agent=threat_detector)
...

# 3. Создаем Crew (команду агентов)
crew = Crew(
    agents=[log_analyzer, threat_detector, ...],
    tasks=[task1, task2, ...],
    process=Process.Sequential  # или Hierarchical
)

# 4. Запускаем
results = crew.kickoff(inputs={...})
```

### Режимы работы:

#### **Sequential Process** (Последовательный):
```
Log Analyzer → Threat Detector → Vulnerability Scanner → 
  Incident Responder → Threat Intelligence
```
Каждый агент ждет завершения предыдущего.

#### **Hierarchical Process** (Иерархический):
```
          Manager Agent
               │
    ┌──────────┼──────────┐
    │          │          │
  Agent1    Agent2     Agent3
```
Менеджер координирует работу подчиненных агентов.

---

## 🗄️ База данных

### ER-диаграмма (упрощенная):

```
┌─────────────────┐         ┌─────────────────┐
│ security_events │         │    threats      │
├─────────────────┤         ├─────────────────┤
│ id (PK)         │────┐    │ id (PK)         │
│ timestamp       │    │    │ event_id (FK)   │
│ source_ip       │    └───►│ threat_type     │
│ event_type      │         │ severity        │
│ raw_log         │         │ confidence      │
└─────────────────┘         └─────────────────┘
                                    │
                                    │
                            ┌───────▼──────────┐
                            │    incidents     │
                            ├──────────────────┤
                            │ id (PK)          │
                            │ threat_id (FK)   │
                            │ status           │
                            │ assigned_to      │
                            └──────────────────┘
                                    │
                                    │
                            ┌───────▼──────────┐
                            │response_actions  │
                            ├──────────────────┤
                            │ id (PK)          │
                            │ incident_id (FK) │
                            │ action_type      │
                            │ executed_at      │
                            └──────────────────┘
```

### Основные таблицы:

1. **security_events** — все события безопасности
2. **threats** — обнаруженные угрозы
3. **indicators_of_compromise** — IoC (IP, domains, hashes)
4. **vulnerabilities** — известные CVE
5. **assets** — инфраструктура
6. **incidents** — инциденты
7. **response_actions** — выполненные действия

Подробнее: [docs/DATABASE.md](DATABASE.md)

---

## 🔄 Workflow и процессы

### Основной workflow:

```
1. 📥 INPUT (Источники данных)
   ├── Логи firewall
   ├── Логи IDS/IPS
   ├── Auth логи
   └── Web-server логи
              ↓
2. 📊 LOG ANALYZER (Агент 1)
   ├── Парсинг логов
   ├── Нормализация
   ├── Enrichment (IP geolocation, reputation)
   └── Корреляция событий
              ↓
3. 🎯 THREAT DETECTOR (Агент 2)
   ├── Signature matching
   ├── Anomaly detection
   ├── Behavior analysis
   └── Threat scoring
              ↓
4. 🔍 VULNERABILITY SCANNER (Агент 3)
   ├── Port scanning
   ├── CVE checking
   ├── Config auditing
   └── Patch status
              ↓
5. ⚡ INCIDENT RESPONDER (Агент 4)
   ├── Classification
   ├── Auto-blocking (L0)
   ├── Semi-auto actions (L1)
   └── Escalation (L2)
              ↓
6. 🌐 THREAT INTELLIGENCE (Агент 5)
   ├── Feed parsing
   ├── IoC enrichment
   ├── CVE monitoring
   └── TTP analysis
              ↓
7. 📤 OUTPUT (Результаты)
   ├── Blocked threats
   ├── Created incidents
   ├── Generated reports
   └── Alerts/notifications
```

---

## 🔗 Интеграции

### External APIs:

1. **VirusTotal** — проверка файлов, IP, доменов
2. **AbuseIPDB** — reputation check для IP
3. **AlienVault OTX** — open threat exchange
4. **NVD (NIST)** — база CVE
5. **MITRE ATT&CK** — TTP mapping

### Internal Integrations:

1. **Firewall** — блокировка IP (через API или SSH)
2. **Active Directory** — управление аккаунтами
3. **Ticketing System** — создание incidents (Jira, ServiceNow)
4. **SIEM** — интеграция с existing SIEM
5. **Slack/Telegram** — уведомления

---

## 📈 Масштабируемость

### Горизонтальное масштабирование:

```
┌─────────────────────────────────────────┐
│          Load Balancer                   │
└──────┬──────────┬──────────┬────────────┘
       │          │          │
   ┌───▼──┐   ┌──▼───┐  ┌──▼───┐
   │ SOC  │   │ SOC  │  │ SOC  │
   │ Node1│   │ Node2│  │ Node3│
   └───┬──┘   └──┬───┘  └──┬───┘
       │          │          │
       └──────────┴──────────┘
                  │
          ┌───────▼────────┐
          │   PostgreSQL   │
          │   (Primary)    │
          └────────────────┘
                  │
        ┌─────────┴─────────┐
    ┌───▼───┐           ┌───▼───┐
    │Replica│           │Replica│
    └───────┘           └───────┘
```

### Вертикальное масштабирование:

- Увеличение CPU/RAM для обработки большего количества events
- Оптимизация SQL запросов
- Caching (Redis) для hot data
- Message Queue (RabbitMQ) для async processing

---

## 🛡️ Security & Compliance

### Security measures:

1. **Authentication** — API keys, OAuth2
2. **Authorization** — RBAC (Role-Based Access Control)
3. **Encryption** — at rest (DB) и in transit (TLS)
4. **Audit logging** — все действия логируются
5. **Input validation** — защита от injection

### Compliance:

- **GDPR** — защита персональных данных
- **PCI DSS** — для финансовых компаний
- **HIPAA** — для здравоохранения
- **ISO 27001** — стандарты ИБ

---

## 📊 Метрики и мониторинг

### Key Metrics:

1. **Events Per Second** (EPS) — пропускная способность
2. **MTTD** (Mean Time To Detect) — среднее время детекции
3. **MTTR** (Mean Time To Respond) — среднее время реагирования
4. **False Positive Rate** — процент ложных срабатываний
5. **Detection Coverage** — покрытие MITRE ATT&CK

### Мониторинг:

- Prometheus — сбор метрик
- Grafana — визуализация
- Alertmanager — алертинг
- Logs — ELK stack (Elasticsearch, Logstash, Kibana)

---

## 🔮 Будущее развитие

### Планируемые улучшения:

1. **ML-модели** — глубокое обучение для детекции
2. **Graph DB** — Neo4j для attack graph analysis
3. **Stream processing** — Apache Kafka для real-time
4. **Auto-remediation** — полностью автономное реагирование
5. **Predictive analytics** — прогнозирование атак

---

## 📚 Дополнительные материалы

- [Описание агентов](AGENTS.md)
- [Инструменты](TOOLS.md)
- [База данных](DATABASE.md)
- [API Reference](API.md)

---

*Архитектура может изменяться в процессе разработки*

**Версия документа**: 1.0  
**Последнее обновление**: 16 августа 2026
