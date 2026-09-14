# 🗄️ AI-SOC: Database Documentation

**Документ**: База данных  
**Версия**: 1.0  
**Дата**: 16 августа 2026

---

## 📋 Содержание

1. [Обзор](#обзор)
2. [ER-диаграмма](#er-диаграмма)
3. [Таблицы](#таблицы)
4. [Индексы](#индексы)
5. [Views](#views)
6. [Миграции](#миграции)

---

## 🎯 Обзор

База данных AI-SOC предназначена для хранения:
- **События безопасности** из различных источников
- **Угрозы** и **инциденты**
- **Индикаторы компрометации** (IoC)
- **Уязвимости** (CVE)
- **Активы** (инфраструктура)
- **Действия по реагированию**

### Поддерживаемые СУБД:
- **PostgreSQL 14+** (production)
- **SQLite 3** (development/testing)

---

## 🏗️ ER-диаграмма

```
┌─────────────────────────────────────────────────────────────────┐
│                      AI-SOC Database Schema                      │
└─────────────────────────────────────────────────────────────────┘

┌──────────────┐         ┌──────────────────┐
│    ASSETS    │◄────────│ SECURITY_EVENTS  │
│              │         │                  │
│ • id         │         │ • id             │
│ • asset_name │         │ • event_timestamp│
│ • asset_type │         │ • source_ip      │
│ • ip_address │         │ • dest_ip        │
│ • criticality│         │ • event_type     │
│ • status     │         │ • severity       │
└───────┬──────┘         └────────┬─────────┘
        │                         │
        │                         │
        │                ┌────────▼─────────┐
        │                │     THREATS      │
        │                │                  │
        │                │ • id             │
        │                │ • threat_type    │
        └────────────────┤ • severity       │
                         │ • source_ip      │
                         │ • status         │
                         │ • mitre_*        │
                         └────────┬─────────┘
                                  │
                                  │
                         ┌────────▼─────────┐
                         │    INCIDENTS     │
                         │                  │
                         │ • id             │
                         │ • incident_number│
                         │ • severity       │
                         │ • status         │
                         │ • assigned_to    │
                         └────────┬─────────┘
                                  │
                                  │
                         ┌────────▼─────────┐
                         │ RESPONSE_ACTIONS │
                         │                  │
                         │ • id             │
                         │ • action_type    │
                         │ • status         │
                         │ • automated      │
                         └──────────────────┘

┌─────────────────────┐    ┌──────────────────┐
│ INDICATORS_OF_      │    │ VULNERABILITIES  │
│ COMPROMISE (IoC)    │    │                  │
│                     │    │ • id             │
│ • id                │    │ • cve_id         │
│ • ioc_type          │    │ • asset_id  ─────┼─┐
│ • ioc_value         │    │ • cvss_score     │ │
│ • threat_type       │    │ • severity       │ │
│ • severity          │    │ • status         │ │
│ • source            │    │ • patch_available│ │
└─────────────────────┘    └──────────────────┘ │
                                                 │
                                                 │
                            ┌────────────────────▼┘
                            │     ASSETS           
                            └──────────────────────
```

---

## 📊 Таблицы

### 1. **assets** - Инфраструктурные активы

**Назначение**: Хранение информации об активах организации

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | UUID/INT | Primary key |
| `asset_name` | VARCHAR(255) | Название актива |
| `asset_type` | VARCHAR(50) | Тип: server, workstation, network_device, etc |
| `ip_address` | INET/TEXT | IP адрес |
| `mac_address` | MACADDR/TEXT | MAC адрес |
| `criticality` | VARCHAR(20) | critical, high, medium, low |
| `status` | VARCHAR(20) | active, inactive, compromised, isolated |
| `os_name` | VARCHAR(100) | Операционная система |
| `owner` | VARCHAR(100) | Владелец |

**Индексы**:
- `idx_assets_ip` на `ip_address`
- `idx_assets_type` на `asset_type`
- `idx_assets_status` на `status`

---

### 2. **security_events** - События безопасности

**Назначение**: Хранение всех событий безопасности из различных источников

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | UUID/INT | Primary key |
| `event_timestamp` | TIMESTAMP | Время события |
| `source_system` | VARCHAR(100) | firewall, ids, waf, auth |
| `source_ip` | INET/TEXT | IP источника |
| `destination_ip` | INET/TEXT | IP назначения |
| `event_type` | VARCHAR(100) | login_attempt, port_scan, etc |
| `event_category` | VARCHAR(50) | authentication, network, malware |
| `severity` | VARCHAR(20) | critical, high, medium, low, info |
| `raw_log` | TEXT | Исходный лог |
| `parsed_data` | JSONB/TEXT | Распарсенные данные |
| `processed` | BOOLEAN | Обработано ли событие |

**Индексы**:
- `idx_events_timestamp` на `event_timestamp` (DESC)
- `idx_events_source_ip` на `source_ip`
- `idx_events_type` на `event_type`
- `idx_events_severity` на `severity`

---

### 3. **indicators_of_compromise** - Индикаторы компрометации

**Назначение**: База known bad indicators (malicious IPs, domains, hashes)

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | UUID/INT | Primary key |
| `ioc_type` | VARCHAR(50) | ip_address, domain, url, file_hash |
| `ioc_value` | TEXT | Значение индикатора |
| `threat_type` | VARCHAR(100) | malware, phishing, c2, botnet |
| `malware_family` | VARCHAR(100) | Название malware |
| `severity` | VARCHAR(20) | critical, high, medium, low |
| `confidence_score` | INTEGER | 0-100 |
| `source` | VARCHAR(100) | VirusTotal, AbuseIPDB, internal |
| `first_seen` | TIMESTAMP | Первое обнаружение |
| `is_active` | BOOLEAN | Активен ли IoC |

**Индексы**:
- `idx_ioc_type` на `ioc_type`
- `idx_ioc_value` на `ioc_value`
- `idx_ioc_active` на `is_active`

**Constraint**: UNIQUE (`ioc_type`, `ioc_value`)

---

### 4. **vulnerabilities** - Уязвимости

**Назначение**: Обнаруженные уязвимости на активах

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | UUID/INT | Primary key |
| `cve_id` | VARCHAR(50) | CVE-2021-44228 |
| `asset_id` | UUID/INT | FK → assets |
| `vulnerability_name` | VARCHAR(255) | Название уязвимости |
| `cvss_score` | DECIMAL(3,1) | 0.0 - 10.0 |
| `severity` | VARCHAR(20) | critical, high, medium, low |
| `exploit_available` | BOOLEAN | Есть ли exploit |
| `patch_available` | BOOLEAN | Доступен ли patch |
| `status` | VARCHAR(50) | open, patched, mitigated |
| `assigned_to` | VARCHAR(100) | Кому назначено |

**Индексы**:
- `idx_vuln_asset` на `asset_id`
- `idx_vuln_cve` на `cve_id`
- `idx_vuln_severity` на `severity`
- `idx_vuln_status` на `status`

---

### 5. **threats** - Угрозы

**Назначение**: Детектированные угрозы (результат анализа событий)

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | UUID/INT | Primary key |
| `source_event_ids` | UUID[]/TEXT | Массив связанных событий |
| `primary_event_id` | UUID/INT | FK → security_events |
| `threat_type` | VARCHAR(100) | brute_force, malware, ddos |
| `threat_category` | VARCHAR(50) | intrusion, malware, dos_ddos |
| `detection_method` | VARCHAR(50) | signature, anomaly, ml_model |
| `severity` | VARCHAR(20) | critical, high, medium, low |
| `confidence_score` | INTEGER | 0-100 |
| `source_ip` | INET/TEXT | IP источника атаки |
| `mitre_tactic` | VARCHAR(100) | Initial Access, Execution |
| `mitre_technique` | VARCHAR(100) | T1078, T1190 |
| `status` | VARCHAR(50) | active, investigating, resolved |

**Индексы**:
- `idx_threats_status` на `status`
- `idx_threats_severity` на `severity`
- `idx_threats_type` на `threat_type`
- `idx_threats_detection` на `detection_timestamp`

---

### 6. **incidents** - Инциденты

**Назначение**: Формализованные инциденты безопасности

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | UUID/INT | Primary key |
| `incident_number` | VARCHAR(50) | INC-2024-001 (UNIQUE) |
| `incident_title` | VARCHAR(255) | Заголовок инцидента |
| `threat_ids` | UUID[]/TEXT | Связанные угрозы |
| `incident_type` | VARCHAR(100) | Тип инцидента |
| `incident_category` | VARCHAR(50) | security_breach, data_loss |
| `severity` | VARCHAR(20) | critical, high, medium, low |
| `status` | VARCHAR(50) | new, investigating, resolved |
| `assigned_to` | VARCHAR(100) | Ответственный |
| `reported_at` | TIMESTAMP | Время создания |
| `resolved_at` | TIMESTAMP | Время решения |
| `sla_deadline` | TIMESTAMP | SLA дедлайн |
| `sla_breached` | BOOLEAN | Нарушен ли SLA |

**Индексы**:
- `idx_incidents_number` на `incident_number`
- `idx_incidents_status` на `status`
- `idx_incidents_severity` на `severity`
- `idx_incidents_reported` на `reported_at` (DESC)

---

### 7. **response_actions** - Действия по реагированию

**Назначение**: Действия, выполненные в ответ на инциденты

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | UUID/INT | Primary key |
| `incident_id` | UUID/INT | FK → incidents |
| `threat_id` | UUID/INT | FK → threats |
| `action_type` | VARCHAR(50) | block_ip, isolate_host, disable_account |
| `action_category` | VARCHAR(50) | containment, eradication, recovery |
| `action_description` | TEXT | Описание действия |
| `target_asset_id` | UUID/INT | FK → assets |
| `status` | VARCHAR(50) | pending, completed, failed |
| `automated` | BOOLEAN | Автоматическое действие? |
| `executed_by` | VARCHAR(100) | Кто выполнил (user/system) |
| `result` | TEXT | Результат выполнения |
| `started_at` | TIMESTAMP | Начало выполнения |
| `completed_at` | TIMESTAMP | Завершение |

**Индексы**:
- `idx_actions_incident` на `incident_id`
- `idx_actions_type` на `action_type`
- `idx_actions_status` на `status`

---

## 🔍 Views (Представления)

### 1. **active_critical_threats**

Показывает активные критические угрозы с информацией об инцидентах и активах.

```sql
SELECT 
    t.*,
    i.incident_number,
    a.asset_name,
    a.ip_address
FROM threats t
LEFT JOIN incidents i ON t.id = ANY(i.threat_ids)
LEFT JOIN assets a ON t.primary_asset_id = a.id
WHERE t.status = 'active' 
  AND t.severity IN ('critical', 'high')
ORDER BY t.detection_timestamp DESC;
```

---

### 2. **incidents_daily_stats**

Статистика инцидентов по дням.

```sql
SELECT 
    DATE(reported_at) as incident_date,
    COUNT(*) as total_incidents,
    COUNT(*) FILTER (WHERE severity = 'critical') as critical_count,
    AVG(resolution_hours) as avg_resolution_hours
FROM incidents
GROUP BY DATE(reported_at);
```

---

### 3. **top_attacking_ips**

Top 100 IP адресов источников угроз.

```sql
SELECT 
    source_ip,
    COUNT(*) as threat_count,
    MAX(severity) as max_severity,
    MIN(first_detected_at) as first_seen
FROM threats
GROUP BY source_ip
ORDER BY threat_count DESC
LIMIT 100;
```

---

## 📈 Типичные запросы

### Найти все события от конкретного IP за последние 24 часа:

```sql
SELECT * FROM security_events
WHERE source_ip = '192.168.1.100'
  AND event_timestamp > NOW() - INTERVAL '24 hours'
ORDER BY event_timestamp DESC;
```

---

### Найти все критические уязвимости без патча:

```sql
SELECT 
    v.*,
    a.asset_name,
    a.ip_address
FROM vulnerabilities v
JOIN assets a ON v.asset_id = a.id
WHERE v.severity = 'critical'
  AND v.patch_available = FALSE
  AND v.status = 'open'
ORDER BY v.cvss_score DESC;
```

---

### Посчитать инциденты по типам за последний месяц:

```sql
SELECT 
    incident_type,
    COUNT(*) as count,
    AVG(EXTRACT(EPOCH FROM (resolved_at - reported_at))/3600) as avg_hours
FROM incidents
WHERE reported_at > NOW() - INTERVAL '1 month'
GROUP BY incident_type
ORDER BY count DESC;
```

---

### Найти все автоматические действия с ошибками:

```sql
SELECT 
    ra.*,
    i.incident_number,
    t.threat_type
FROM response_actions ra
JOIN incidents i ON ra.incident_id = i.id
LEFT JOIN threats t ON ra.threat_id = t.id
WHERE ra.automated = TRUE
  AND ra.status = 'failed'
ORDER BY ra.created_at DESC;
```

---

## 🔧 Миграции

### Инициализация базы данных:

**PostgreSQL**:
```bash
psql -U postgres -d ai_soc < database/schema.sql
```

**SQLite**:
```bash
sqlite3 database/ai_soc.db < database/schema_sqlite.sql
```

---

### Создание базы данных PostgreSQL:

```sql
CREATE DATABASE ai_soc
    WITH 
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.UTF-8'
    LC_CTYPE = 'en_US.UTF-8'
    TEMPLATE = template0;
```

---

## 🛡️ Best Practices

### 1. **Индексы**
- Все FK колонки проиндексированы
- Индексы на часто используемых фильтрах (severity, status, timestamp)
- Composite индексы для сложных запросов

### 2. **Partitioning** (для больших объемов)
Рекомендуется партиционирование `security_events` по дате:

```sql
-- Пример партиционирования по месяцам
CREATE TABLE security_events_2024_08 
PARTITION OF security_events
FOR VALUES FROM ('2024-08-01') TO ('2024-09-01');
```

### 3. **Retention Policy**
- `security_events`: хранить 90 дней, затем архивировать
- `threats`: хранить 1 год
- `incidents`: хранить постоянно
- `response_actions`: хранить постоянно (audit trail)

### 4. **Backup**
```bash
# PostgreSQL backup
pg_dump -U postgres ai_soc > backup_$(date +%Y%m%d).sql

# SQLite backup
sqlite3 database/ai_soc.db ".backup backup_$(date +%Y%m%d).db"
```

---

## 📊 Размер данных (estimates)

| Таблица | Средний размер записи | 1M записей |
|---------|----------------------|------------|
| security_events | ~2 KB | ~2 GB |
| threats | ~1 KB | ~1 GB |
| incidents | ~1.5 KB | ~1.5 GB |
| response_actions | ~0.5 KB | ~500 MB |
| vulnerabilities | ~1 KB | ~1 GB |
| IoC | ~0.5 KB | ~500 MB |
| assets | ~0.5 KB | ~500 MB |

**Общий размер при 1M событий в день**: ~7.5 GB/day

---

## 🔮 Будущие улучшения

1. **Time-series DB** - для security_events (InfluxDB, TimescaleDB)
2. **Graph DB** - для attack graph analysis (Neo4j)
3. **Full-text search** - Elasticsearch для логов
4. **Data Lake** - S3/MinIO для архивных данных
5. **Real-time streams** - Kafka для streaming events

---

*База данных может изменяться в процессе разработки*

**Версия документа**: 1.0  
**Последнее обновление**: 16 августа 2026
