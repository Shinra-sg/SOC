# Test Data Generators

Генераторы тестовых данных для AI-SOC системы.

## Структура

```
data/
├── generators/          # Скрипты генерации данных
│   ├── generate_assets.py         # Mock инфраструктура
│   ├── generate_ioc.py            # Indicators of Compromise
│   └── generate_cve.py            # CVE уязвимости
├── samples/            # Сгенерированные данные
│   ├── assets.json
│   ├── assets.sql
│   ├── ioc.json
│   ├── ioc.sql
│   ├── vulnerabilities.json
│   └── vulnerabilities.sql
└── README.md
```

## Генераторы

### 1. generate_assets.py

Генерирует mock инфраструктуру (серверы, workstations, network devices).

**Использование:**
```bash
python3 data/generators/generate_assets.py
```

**Параметры (в коде):**
- `count` — количество assets (по умолчанию: 50)

**Генерирует:**
- 30% servers (web, app, db, mail, file, backup, etc.)
- 50% workstations (Windows, macOS, Linux)
- 15% network devices (switches, routers, firewalls)
- 5% mobile devices

**Атрибуты:**
- IP address, MAC address, hostname
- OS name and version
- Criticality (critical, high, medium, low)
- Status (active, inactive, maintenance)
- Owner, department, location
- Last patch date

**Вывод:**
- `data/samples/assets.json`
- `data/samples/assets.sql`

---

### 2. generate_ioc.py

Генерирует Indicators of Compromise (malicious IPs, domains, file hashes).

**Использование:**
```bash
python3 data/generators/generate_ioc.py
```

**Параметры (в коде):**
- `count` — количество IoC (по умолчанию: 100)

**Генерирует:**
- 40% malicious IP addresses
- 30% phishing/malicious domains
- 25% file hashes (MD5, SHA1, SHA256)
- 5% malicious URLs

**Threat Types:**
- malware, phishing, c2, botnet, ransomware
- trojan, backdoor, spyware, adware, exploit

**Атрибуты:**
- Threat type, malware family
- Severity, confidence score (0-100)
- Source (VirusTotal, AbuseIPDB, etc.)
- First/last seen dates
- MITRE ATT&CK mapping
- Active status

**Вывод:**
- `data/samples/ioc.json`
- `data/samples/ioc.sql`

---

### 3. generate_cve.py

Генерирует уязвимости (CVE) на assets.

**Использование:**
```bash
python3 data/generators/generate_cve.py
```

**Параметры (в коде):**
- `assets_count` — количество assets (должно совпадать с generate_assets)
- `vuln_per_asset_max` — максимум уязвимостей на asset (по умолчанию: 3)

**Известные CVE:**
- CVE-2021-44228 (Log4Shell) - CVSS 10.0
- CVE-2022-22965 (Spring4Shell) - CVSS 9.8
- CVE-2020-1472 (Zerologon) - CVSS 10.0
- CVE-2019-0708 (BlueKeep) - CVSS 9.8
- CVE-2017-0144 (EternalBlue) - CVSS 8.1
- И другие реальные CVE

**Атрибуты:**
- CVE ID, CVSS score, severity
- Affected software and version
- Exploit availability (public/private)
- Patch availability and version
- Status (open, patched, mitigated, etc.)
- Priority, due date, assignment
- Remediation steps, workarounds

**Вывод:**
- `data/samples/vulnerabilities.json`
- `data/samples/vulnerabilities.sql`

---

## Генерация всех данных

Чтобы сгенерировать все данные сразу:

```bash
# Из корня проекта
cd /path/to/ai-soc

# Генерируем все
python3 data/generators/generate_assets.py
python3 data/generators/generate_ioc.py
python3 data/generators/generate_cve.py
```

Или создай bash скрипт:

```bash
#!/bin/bash
# generate_all.sh

echo "Generating test data..."

python3 data/generators/generate_assets.py
python3 data/generators/generate_ioc.py
python3 data/generators/generate_cve.py

echo "Done! Check data/samples/"
```

---

## Загрузка в базу данных

### SQLite

```bash
# Загрузить assets
sqlite3 database/ai_soc.db < data/samples/assets.sql

# Загрузить IoC
sqlite3 database/ai_soc.db < data/samples/ioc.sql

# Загрузить vulnerabilities
sqlite3 database/ai_soc.db < data/samples/vulnerabilities.sql
```

### PostgreSQL

```bash
# Загрузить assets
psql -U postgres -d ai_soc < data/samples/assets.sql

# Загрузить IoC
psql -U postgres -d ai_soc < data/samples/ioc.sql

# Загрузить vulnerabilities
psql -U postgres -d ai_soc < data/samples/vulnerabilities.sql
```

---

## Статистика сгенерированных данных

### Assets (50 total)
- Servers: ~15 (web, app, db, mail, file, backup)
- Workstations: ~25 (Windows, macOS, Linux)
- Network devices: ~7 (switches, routers, firewalls)
- Mobile: ~3 (iOS, Android)

### IoC (100 total)
- Malicious IPs: ~40
- Phishing domains: ~30
- File hashes: ~25
- Malicious URLs: ~5

**По severity:**
- Critical: ~20%
- High: ~30%
- Medium: ~30%
- Low: ~20%

### Vulnerabilities (50-100 total)
Зависит от количества assets и настроек.

**По severity:**
- Critical: ~35%
- High: ~35%
- Medium: ~20%
- Low: ~10%

**Статус:**
- Open: ~40%
- In Progress: ~20%
- Patched: ~25%
- Mitigated: ~10%
- Accepted Risk: ~5%

---

## Кастомизация

Чтобы изменить параметры генерации, отредактируй переменные в скриптах:

**generate_assets.py:**
```python
# Изменить количество
assets = generate_assets(count=100)  # вместо 50
```

**generate_ioc.py:**
```python
# Изменить количество и типы
iocs = generate_iocs(count=200)  # вместо 100
```

**generate_cve.py:**
```python
# Изменить количество уязвимостей
vulnerabilities = generate_cve_vulnerabilities(
    assets_count=100,      # вместо 50
    vuln_per_asset_max=5   # вместо 3
)
```

---

## Примеры данных

### Asset Example
```json
{
  "asset_name": "web-server-01",
  "asset_type": "server",
  "ip_address": "192.168.1.10",
  "hostname": "web01.company.local",
  "criticality": "critical",
  "os_name": "Ubuntu 22.04",
  "status": "active"
}
```

### IoC Example
```json
{
  "ioc_type": "ip_address",
  "ioc_value": "45.142.212.100",
  "threat_type": "malware",
  "malware_family": "Emotet",
  "severity": "high",
  "confidence_score": 95
}
```

### Vulnerability Example
```json
{
  "cve_id": "CVE-2021-44228",
  "vulnerability_name": "Log4Shell",
  "cvss_score": 10.0,
  "severity": "critical",
  "exploit_available": true,
  "patch_available": true,
  "status": "open"
}
```

---

## Интеграция с тестами

Эти данные используются в:
- `database/test_realistic_data.py` — тестирование БД
- `tests/integration/` — интеграционные тесты
- `tests/scenarios/` — тесты сценариев атак

---

## Лицензия

MIT License
