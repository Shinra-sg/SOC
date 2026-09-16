# Database Layer Documentation

Документация по работе с Database Layer в AI-SOC.

## Архитектура

Database Layer построен на базе SQLAlchemy ORM и использует Repository Pattern для изоляции бизнес-логики от деталей хранения данных.

```
┌─────────────────────────────────────────┐
│         Application Layer               │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│      Repository Layer (CRUD)            │
│  - AssetRepository                      │
│  - SecurityEventRepository              │
│  - IoC_Repository                       │
│  - VulnerabilityRepository              │
│  - ThreatRepository                     │
│  - IncidentRepository                   │
│  - ResponseActionRepository             │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│         ORM Models                      │
│  - Asset, SecurityEvent, IoC, etc.      │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│      Connection Pool                    │
│  - PostgreSQL / SQLite                  │
└─────────────────────────────────────────┘
```

## Компоненты

### 1. Connection Management (`connection.py`)

Управление подключениями к базе данных.

**Основные классы:**
- `DatabaseConnection` - Singleton для управления connection pool
- `Base` - Base class для всех ORM моделей

**Использование:**

```python
from ai_soc.database import db, session_scope

# Context manager (автоматический commit/rollback)
with session_scope() as session:
    asset = Asset(asset_name='server-01', asset_type='server')
    session.add(asset)
    # Автоматический commit при выходе из блока
```

**Конфигурация:**

Через переменные окружения (.env):

```bash
# SQLite (development)
DB_TYPE=sqlite
DB_PATH=database/ai_soc.db

# PostgreSQL (production)
DB_TYPE=postgresql
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ai_soc
DB_USER=postgres
DB_PASSWORD=your_password
```

---

### 2. ORM Models (`models.py`)

SQLAlchemy модели для всех таблиц.

**Модели:**

1. **Asset** - Инфраструктурные активы
2. **SecurityEvent** - События безопасности
3. **IndicatorOfCompromise** - Индикаторы компрометации
4. **Vulnerability** - Уязвимости (CVE)
5. **Threat** - Обнаруженные угрозы
6. **Incident** - Инциденты безопасности
7. **ResponseAction** - Действия по реагированию

**Пример модели:**

```python
class Asset(Base):
    __tablename__ = 'assets'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    asset_name: Mapped[str] = mapped_column(String(255))
    asset_type: Mapped[str] = mapped_column(String(50))
    ip_address: Mapped[Optional[str]] = mapped_column(String(45))
    criticality: Mapped[str] = mapped_column(String(20))
    
    # Relationships
    vulnerabilities: Mapped[List["Vulnerability"]] = relationship(...)
```

---

### 3. Repositories (`repositories.py`)

Repository Pattern для CRUD операций.

**Base Repository:**

Все repositories наследуются от `BaseRepository` с базовыми методами:
- `get_by_id(id)` - Получить по ID
- `get_all(limit, offset)` - Получить все
- `create(**kwargs)` - Создать
- `update(id, **kwargs)` - Обновить
- `delete(id)` - Удалить
- `count()` - Подсчитать

**Специализированные методы:**

Каждый repository добавляет свои методы:

```python
# AssetRepository
repo.get_by_ip(ip_address)
repo.get_by_type(asset_type)
repo.get_critical_assets()
repo.get_compromised_assets()
repo.search(query)

# SecurityEventRepository
repo.get_unprocessed()
repo.get_critical_events()
repo.get_by_source_ip(source_ip)
repo.mark_as_processed(event_id)
repo.get_statistics()

# IoC_Repository
repo.check_ip(ip_address)
repo.check_domain(domain)
repo.check_hash(file_hash)
repo.get_active()

# VulnerabilityRepository
repo.get_by_asset(asset_id)
repo.get_critical()
repo.get_with_public_exploit()
repo.get_actively_exploited()
```

---

## Примеры использования

### 1. Создание и чтение Asset

```python
from ai_soc.database import session_scope, AssetRepository

with session_scope() as session:
    repo = AssetRepository(session)
    
    # CREATE
    asset = repo.create(
        asset_name='web-server-01',
        asset_type='server',
        ip_address='192.168.1.10',
        criticality='critical',
        status='active'
    )
    
    print(f"Created: {asset.id}")

# READ
with session_scope() as session:
    repo = AssetRepository(session)
    asset = repo.get_by_ip('192.168.1.10')
    print(f"Found: {asset.asset_name}")
```

### 2. Обработка Security Events

```python
from ai_soc.database import session_scope, SecurityEventRepository

with session_scope() as session:
    repo = SecurityEventRepository(session)
    
    # Получить необработанные события
    unprocessed = repo.get_unprocessed(limit=10)
    
    for event in unprocessed:
        # Обработать событие
        process_event(event)
        
        # Отметить как обработанное
        repo.mark_as_processed(event.id)
```

### 3. Проверка IP в IoC

```python
from ai_soc.database import session_scope, IoC_Repository

def check_malicious_ip(ip_address: str) -> bool:
    with session_scope() as session:
        repo = IoC_Repository(session)
        ioc = repo.check_ip(ip_address)
        
        if ioc:
            print(f"⚠️  Malicious IP detected!")
            print(f"   Type: {ioc.threat_type}")
            print(f"   Severity: {ioc.severity}")
            print(f"   Confidence: {ioc.confidence_score}%")
            return True
        
        return False

# Использование
if check_malicious_ip('45.142.212.100'):
    # Блокировать IP
    block_ip('45.142.212.100')
```

### 4. Работа с уязвимостями

```python
from ai_soc.database import session_scope, VulnerabilityRepository

with session_scope() as session:
    repo = VulnerabilityRepository(session)
    
    # Получить критичные уязвимости
    critical_vulns = repo.get_critical()
    
    for vuln in critical_vulns:
        print(f"CVE: {vuln.cve_id}")
        print(f"CVSS: {vuln.cvss_score}")
        print(f"Asset: {vuln.asset.asset_name}")
        
        if vuln.actively_exploited:
            # Срочно патчить!
            patch_asset(vuln.asset_id)
```

### 5. Использование RepositoryFactory

```python
from ai_soc.database import session_scope, RepositoryFactory

with session_scope() as session:
    factory = RepositoryFactory(session)
    
    # Доступ ко всем repositories через фабрику
    assets = factory.assets.get_critical_assets()
    events = factory.events.get_critical_events()
    threats = factory.threats.get_active()
    incidents = factory.incidents.get_open()
    
    print(f"Critical assets: {len(assets)}")
    print(f"Critical events: {len(events)}")
    print(f"Active threats: {len(threats)}")
    print(f"Open incidents: {len(incidents)}")
```

### 6. Создание инцидента с действиями

```python
from ai_soc.database import session_scope, IncidentRepository, ResponseActionRepository

with session_scope() as session:
    incident_repo = IncidentRepository(session)
    action_repo = ResponseActionRepository(session)
    
    # Создать инцидент
    incident = incident_repo.create(
        incident_number=incident_repo.generate_incident_number(),
        incident_title='Brute Force Attack Detected',
        incident_type='unauthorized_access_attempt',
        severity='high',
        status='investigating',
        description='Multiple failed login attempts detected'
    )
    
    # Создать автоматическое действие
    action = action_repo.create(
        incident_id=incident.id,
        action_type='block_ip',
        action_category='containment',
        action_description='Block malicious IP in firewall',
        target_ip='45.142.212.100',
        automated=True,
        status='pending'
    )
    
    print(f"Incident {incident.incident_number} created")
    print(f"Action {action.id} scheduled")
```

---

## Best Practices

### 1. Всегда используйте context manager

```python
# ✅ Правильно
with session_scope() as session:
    repo = AssetRepository(session)
    asset = repo.get_by_id(1)

# ❌ Неправильно
session = db.create_session()
repo = AssetRepository(session)
asset = repo.get_by_id(1)
# session никогда не закрывается!
```

### 2. Используйте repositories вместо прямых запросов

```python
# ✅ Правильно
with session_scope() as session:
    repo = AssetRepository(session)
    asset = repo.get_by_ip('192.168.1.10')

# ❌ Неправильно
with session_scope() as session:
    asset = session.query(Asset).filter(Asset.ip_address == '192.168.1.10').first()
```

### 3. Используйте transactions для связанных операций

```python
with session_scope() as session:
    # Все операции в одной транзакции
    incident = incident_repo.create(...)
    action1 = action_repo.create(incident_id=incident.id, ...)
    action2 = action_repo.create(incident_id=incident.id, ...)
    # Автоматический commit при выходе
```

### 4. Обрабатывайте ошибки

```python
from sqlalchemy.exc import IntegrityError

try:
    with session_scope() as session:
        repo = AssetRepository(session)
        asset = repo.create(...)
except IntegrityError:
    print("Asset with this IP already exists")
```

---

## Тестирование

Запуск тестов Database Layer:

```bash
# Простой тест (без pytest)
python3 database/test_db_layer.py

# С pytest (если установлен)
pytest tests/test_database.py -v
```

---

## Performance Tips

### 1. Используйте limit для больших выборок

```python
events = repo.get_all(limit=100)  # Вместо всех записей
```

### 2. Используйте eager loading для relationships

```python
from sqlalchemy.orm import joinedload

assets = session.query(Asset).options(
    joinedload(Asset.vulnerabilities)
).all()
```

### 3. Используйте bulk operations для массовых вставок

```python
# Для массовых вставок
session.bulk_insert_mappings(Asset, [
    {'asset_name': 'server-1', 'asset_type': 'server'},
    {'asset_name': 'server-2', 'asset_type': 'server'},
    # ... еще 1000 записей
])
session.commit()
```

---

## Миграции

Для изменения схемы БД используйте Alembic (опционально).

Установка:
```bash
pip install alembic
alembic init alembic
```

Создание миграции:
```bash
alembic revision --autogenerate -m "Add new field"
alembic upgrade head
```

---

## Troubleshooting

### Проблема: "No module named 'ai_soc.database'"

**Решение**: Убедитесь что путь к src добавлен:
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
```

### Проблема: "PRAGMA foreign_keys not enabled"

**Решение**: Для SQLite foreign keys включаются автоматически в connection.py

### Проблема: "Connection pool timeout"

**Решение**: Проверьте что все sessions закрываются правильно (используйте context manager)

---

## См. также

- [DATABASE.md](DATABASE.md) - Схема базы данных
- [ARCHITECTURE.md](../ARCHITECTURE.md) - Общая архитектура системы
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
