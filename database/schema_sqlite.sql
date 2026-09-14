-- ============================================================================
-- AI-SOC Database Schema - SQLite Version
-- Security Operations Center - Database Design (for development)
-- Version: 1.0
-- Date: 2026-08-16
-- ============================================================================

-- Примечание: SQLite версия упрощена по сравнению с PostgreSQL
-- Нет UUID (используем INTEGER PRIMARY KEY), нет INET/MACADDR типов

-- ============================================================================
-- 1. ASSETS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS assets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Основная информация
    asset_name TEXT NOT NULL,
    asset_type TEXT NOT NULL CHECK (asset_type IN (
        'server', 'workstation', 'network_device', 
        'mobile', 'iot', 'application', 'database'
    )),
    
    -- Сетевые параметры
    ip_address TEXT,
    mac_address TEXT,
    hostname TEXT,
    
    -- Классификация
    criticality TEXT DEFAULT 'medium' CHECK (criticality IN (
        'critical', 'high', 'medium', 'low'
    )),
    business_unit TEXT,
    location TEXT,
    
    -- Технические параметры
    os_name TEXT,
    os_version TEXT,
    last_patch_date TEXT,
    
    -- Статус
    status TEXT DEFAULT 'active' CHECK (status IN (
        'active', 'inactive', 'maintenance', 'compromised', 'isolated'
    )),
    
    -- Владение и ответственность
    owner TEXT,
    assigned_team TEXT,
    
    -- Метаданные
    metadata TEXT, -- JSON as TEXT
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    
    UNIQUE (ip_address, mac_address)
);

CREATE INDEX idx_assets_ip ON assets(ip_address);
CREATE INDEX idx_assets_type ON assets(asset_type);
CREATE INDEX idx_assets_status ON assets(status);

-- ============================================================================
-- 2. SECURITY_EVENTS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS security_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Временные метки
    event_timestamp TEXT NOT NULL,
    received_at TEXT DEFAULT (datetime('now')),
    
    -- Источник события
    source_system TEXT NOT NULL,
    source_ip TEXT,
    source_port INTEGER,
    source_asset_id INTEGER REFERENCES assets(id),
    
    -- Назначение
    destination_ip TEXT,
    destination_port INTEGER,
    destination_asset_id INTEGER REFERENCES assets(id),
    
    -- Классификация события
    event_type TEXT NOT NULL,
    event_category TEXT NOT NULL CHECK (event_category IN (
        'authentication', 'network', 'malware', 'data_access',
        'system', 'application', 'policy_violation', 'anomaly'
    )),
    
    -- Severity
    severity TEXT DEFAULT 'medium' CHECK (severity IN (
        'critical', 'high', 'medium', 'low', 'info'
    )),
    
    -- Детали
    event_description TEXT,
    raw_log TEXT,
    parsed_data TEXT, -- JSON
    
    -- Пользовательский контекст
    username TEXT,
    user_agent TEXT,
    
    -- Протокол и действие
    protocol TEXT,
    action_taken TEXT,
    
    -- Обработка
    processed INTEGER DEFAULT 0,
    false_positive INTEGER DEFAULT 0,
    
    -- Метаданные
    tags TEXT, -- JSON array
    metadata TEXT, -- JSON
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX idx_events_timestamp ON security_events(event_timestamp);
CREATE INDEX idx_events_source_ip ON security_events(source_ip);
CREATE INDEX idx_events_type ON security_events(event_type);
CREATE INDEX idx_events_severity ON security_events(severity);

-- ============================================================================
-- 3. INDICATORS_OF_COMPROMISE TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS indicators_of_compromise (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Тип и значение
    ioc_type TEXT NOT NULL CHECK (ioc_type IN (
        'ip_address', 'domain', 'url', 'file_hash', 
        'email', 'registry_key', 'mutex', 'certificate'
    )),
    ioc_value TEXT NOT NULL,
    hash_type TEXT,
    
    -- Классификация угрозы
    threat_type TEXT,
    malware_family TEXT,
    
    -- Severity и confidence
    severity TEXT DEFAULT 'medium' CHECK (severity IN (
        'critical', 'high', 'medium', 'low'
    )),
    confidence_score INTEGER CHECK (confidence_score >= 0 AND confidence_score <= 100),
    
    -- Источник
    source TEXT NOT NULL,
    source_url TEXT,
    
    -- Временные рамки
    first_seen TEXT,
    last_seen TEXT,
    expires_at TEXT,
    
    -- Контекст
    description TEXT,
    attack_pattern TEXT,
    
    -- Статус
    is_active INTEGER DEFAULT 1,
    false_positive INTEGER DEFAULT 0,
    
    -- Метаданные
    tags TEXT, -- JSON
    metadata TEXT, -- JSON
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    
    UNIQUE (ioc_type, ioc_value)
);

CREATE INDEX idx_ioc_type ON indicators_of_compromise(ioc_type);
CREATE INDEX idx_ioc_value ON indicators_of_compromise(ioc_value);
CREATE INDEX idx_ioc_active ON indicators_of_compromise(is_active);

-- ============================================================================
-- 4. VULNERABILITIES TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS vulnerabilities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- CVE информация
    cve_id TEXT,
    cve_published_date TEXT,
    
    -- Затронутый актив
    asset_id INTEGER NOT NULL REFERENCES assets(id) ON DELETE CASCADE,
    
    -- Описание
    vulnerability_name TEXT NOT NULL,
    description TEXT,
    
    -- Severity
    cvss_score REAL CHECK (cvss_score >= 0 AND cvss_score <= 10),
    cvss_vector TEXT,
    severity TEXT CHECK (severity IN (
        'critical', 'high', 'medium', 'low', 'info'
    )),
    
    -- Категория
    vulnerability_type TEXT,
    category TEXT,
    
    -- Затронутое ПО
    affected_software TEXT,
    affected_version TEXT,
    
    -- Эксплойты
    exploit_available INTEGER DEFAULT 0,
    exploit_public INTEGER DEFAULT 0,
    actively_exploited INTEGER DEFAULT 0,
    
    -- Remediation
    patch_available INTEGER DEFAULT 0,
    patch_version TEXT,
    remediation_steps TEXT,
    workaround TEXT,
    
    -- Статус
    status TEXT DEFAULT 'open' CHECK (status IN (
        'open', 'in_progress', 'patched', 'mitigated', 
        'accepted_risk', 'false_positive', 'closed'
    )),
    
    -- Приоритет
    priority TEXT DEFAULT 'medium' CHECK (priority IN (
        'critical', 'high', 'medium', 'low'
    )),
    due_date TEXT,
    
    -- Назначение
    assigned_to TEXT,
    assigned_team TEXT,
    
    -- Сканирование
    scan_date TEXT,
    scanner_name TEXT,
    
    -- Даты
    discovered_at TEXT DEFAULT (datetime('now')),
    resolved_at TEXT,
    verified_at TEXT,
    
    -- Метаданные
    tags TEXT, -- JSON
    metadata TEXT, -- JSON
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX idx_vuln_asset ON vulnerabilities(asset_id);
CREATE INDEX idx_vuln_cve ON vulnerabilities(cve_id);
CREATE INDEX idx_vuln_severity ON vulnerabilities(severity);
CREATE INDEX idx_vuln_status ON vulnerabilities(status);

-- ============================================================================
-- 5. THREATS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS threats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Связь с событиями
    source_event_ids TEXT, -- JSON array
    primary_event_id INTEGER REFERENCES security_events(id),
    
    -- Затронутые активы
    affected_asset_ids TEXT, -- JSON array
    primary_asset_id INTEGER REFERENCES assets(id),
    
    -- Классификация угрозы
    threat_type TEXT NOT NULL,
    threat_category TEXT NOT NULL CHECK (threat_category IN (
        'intrusion', 'malware', 'dos_ddos', 'data_breach',
        'insider_threat', 'phishing', 'exploit', 'anomaly'
    )),
    threat_name TEXT,
    
    -- Детекция
    detection_method TEXT CHECK (detection_method IN (
        'signature', 'anomaly', 'behavioral', 'ml_model', 'manual'
    )),
    detection_timestamp TEXT DEFAULT (datetime('now')),
    
    -- Severity и confidence
    severity TEXT DEFAULT 'medium' CHECK (severity IN (
        'critical', 'high', 'medium', 'low'
    )),
    confidence_score INTEGER CHECK (confidence_score >= 0 AND confidence_score <= 100),
    risk_score INTEGER CHECK (risk_score >= 0 AND risk_score <= 100),
    
    -- Источник угрозы
    source_ip TEXT,
    source_country TEXT,
    source_geolocation TEXT,
    
    -- Целевые параметры
    target_ip TEXT,
    target_port INTEGER,
    attack_vector TEXT,
    
    -- MITRE ATT&CK
    mitre_tactic TEXT,
    mitre_technique TEXT,
    mitre_subtechnique TEXT,
    
    -- Описание
    description TEXT,
    technical_details TEXT,
    indicators TEXT, -- JSON
    
    -- Статус
    status TEXT DEFAULT 'active' CHECK (status IN (
        'active', 'investigating', 'contained', 
        'resolved', 'false_positive', 'monitoring'
    )),
    
    -- Временная линия
    first_detected_at TEXT,
    last_detected_at TEXT,
    resolved_at TEXT,
    
    -- False positive
    false_positive INTEGER DEFAULT 0,
    false_positive_reason TEXT,
    
    -- Метаданные
    tags TEXT, -- JSON
    metadata TEXT, -- JSON
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX idx_threats_status ON threats(status);
CREATE INDEX idx_threats_severity ON threats(severity);
CREATE INDEX idx_threats_type ON threats(threat_type);
CREATE INDEX idx_threats_detection ON threats(detection_timestamp);

-- ============================================================================
-- 6. INCIDENTS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS incidents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Идентификация
    incident_number TEXT UNIQUE NOT NULL,
    incident_title TEXT NOT NULL,
    
    -- Связанные угрозы и события
    threat_ids TEXT, -- JSON array
    primary_threat_id INTEGER REFERENCES threats(id),
    event_count INTEGER DEFAULT 0,
    
    -- Классификация
    incident_type TEXT NOT NULL,
    incident_category TEXT CHECK (incident_category IN (
        'security_breach', 'data_loss', 'service_disruption',
        'policy_violation', 'malware_infection', 'unauthorized_access'
    )),
    
    -- Severity и impact
    severity TEXT DEFAULT 'medium' CHECK (severity IN (
        'critical', 'high', 'medium', 'low'
    )),
    impact TEXT CHECK (impact IN (
        'critical', 'high', 'medium', 'low', 'none'
    )),
    urgency TEXT CHECK (urgency IN (
        'critical', 'high', 'medium', 'low'
    )),
    
    -- Scope
    affected_asset_ids TEXT, -- JSON array
    affected_users TEXT, -- JSON array
    affected_systems_count INTEGER DEFAULT 0,
    
    -- Описание
    description TEXT NOT NULL,
    attack_narrative TEXT,
    business_impact TEXT,
    
    -- Статус
    status TEXT DEFAULT 'new' CHECK (status IN (
        'new', 'assigned', 'investigating', 'containing',
        'eradicating', 'recovering', 'resolved', 'closed'
    )),
    
    -- Назначение
    assigned_to TEXT,
    assigned_team TEXT,
    escalation_level INTEGER DEFAULT 1 CHECK (escalation_level BETWEEN 1 AND 3),
    
    -- Timeline
    reported_at TEXT DEFAULT (datetime('now')),
    acknowledged_at TEXT,
    started_at TEXT,
    contained_at TEXT,
    resolved_at TEXT,
    closed_at TEXT,
    
    -- SLA
    sla_deadline TEXT,
    sla_breached INTEGER DEFAULT 0,
    
    -- Root cause
    root_cause TEXT,
    lessons_learned TEXT,
    
    -- Метаданные
    tags TEXT, -- JSON
    metadata TEXT, -- JSON
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX idx_incidents_number ON incidents(incident_number);
CREATE INDEX idx_incidents_status ON incidents(status);
CREATE INDEX idx_incidents_severity ON incidents(severity);
CREATE INDEX idx_incidents_reported ON incidents(reported_at);

-- ============================================================================
-- 7. RESPONSE_ACTIONS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS response_actions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Связь с инцидентом
    incident_id INTEGER NOT NULL REFERENCES incidents(id) ON DELETE CASCADE,
    threat_id INTEGER REFERENCES threats(id),
    
    -- Тип действия
    action_type TEXT NOT NULL CHECK (action_type IN (
        'block_ip', 'isolate_host', 'disable_account', 
        'kill_process', 'quarantine_file', 'update_firewall',
        'reset_password', 'revoke_access', 'backup_data',
        'collect_evidence', 'notify', 'escalate', 'manual_intervention'
    )),
    action_category TEXT CHECK (action_category IN (
        'containment', 'eradication', 'recovery', 'investigation', 'notification'
    )),
    
    -- Описание
    action_description TEXT NOT NULL,
    action_details TEXT, -- JSON
    
    -- Целевые объекты
    target_asset_id INTEGER REFERENCES assets(id),
    target_ip TEXT,
    target_user TEXT,
    target_identifiers TEXT, -- JSON
    
    -- Статус
    status TEXT DEFAULT 'pending' CHECK (status IN (
        'pending', 'in_progress', 'completed', 'failed', 'rolled_back', 'cancelled'
    )),
    
    -- Автоматизация
    automated INTEGER DEFAULT 0,
    auto_approved INTEGER DEFAULT 0,
    requires_approval INTEGER DEFAULT 0,
    approved_by TEXT,
    approved_at TEXT,
    
    -- Исполнение
    executed_by TEXT,
    execution_method TEXT,
    
    -- Результат
    result TEXT,
    success INTEGER,
    error_message TEXT,
    
    -- Временные метки
    scheduled_at TEXT,
    started_at TEXT,
    completed_at TEXT,
    
    -- Rollback
    rollback_possible INTEGER DEFAULT 0,
    rollback_action_id INTEGER REFERENCES response_actions(id),
    
    -- Метаданные
    tags TEXT, -- JSON
    metadata TEXT, -- JSON
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX idx_actions_incident ON response_actions(incident_id);
CREATE INDEX idx_actions_threat ON response_actions(threat_id);
CREATE INDEX idx_actions_type ON response_actions(action_type);
CREATE INDEX idx_actions_status ON response_actions(status);

-- ============================================================================
-- TRIGGERS для updated_at
-- ============================================================================

CREATE TRIGGER update_assets_updated_at 
AFTER UPDATE ON assets
FOR EACH ROW
BEGIN
    UPDATE assets SET updated_at = datetime('now') WHERE id = NEW.id;
END;

CREATE TRIGGER update_ioc_updated_at 
AFTER UPDATE ON indicators_of_compromise
FOR EACH ROW
BEGIN
    UPDATE indicators_of_compromise SET updated_at = datetime('now') WHERE id = NEW.id;
END;

CREATE TRIGGER update_vulnerabilities_updated_at 
AFTER UPDATE ON vulnerabilities
FOR EACH ROW
BEGIN
    UPDATE vulnerabilities SET updated_at = datetime('now') WHERE id = NEW.id;
END;

CREATE TRIGGER update_threats_updated_at 
AFTER UPDATE ON threats
FOR EACH ROW
BEGIN
    UPDATE threats SET updated_at = datetime('now') WHERE id = NEW.id;
END;

CREATE TRIGGER update_incidents_updated_at 
AFTER UPDATE ON incidents
FOR EACH ROW
BEGIN
    UPDATE incidents SET updated_at = datetime('now') WHERE id = NEW.id;
END;

CREATE TRIGGER update_response_actions_updated_at 
AFTER UPDATE ON response_actions
FOR EACH ROW
BEGIN
    UPDATE response_actions SET updated_at = datetime('now') WHERE id = NEW.id;
END;

-- ============================================================================
-- VIEWS для аналитики
-- ============================================================================

-- View: Активные критические угрозы
CREATE VIEW IF NOT EXISTS active_critical_threats AS
SELECT 
    t.*,
    i.incident_number,
    a.asset_name,
    a.ip_address
FROM threats t
LEFT JOIN incidents i ON instr(i.threat_ids, t.id) > 0
LEFT JOIN assets a ON t.primary_asset_id = a.id
WHERE t.status = 'active' 
  AND t.severity IN ('critical', 'high')
ORDER BY t.detection_timestamp DESC;

-- View: Top атакующие IP
CREATE VIEW IF NOT EXISTS top_attacking_ips AS
SELECT 
    source_ip,
    COUNT(*) as threat_count,
    MAX(severity) as max_severity,
    MIN(first_detected_at) as first_seen,
    MAX(last_detected_at) as last_seen
FROM threats
WHERE source_ip IS NOT NULL
GROUP BY source_ip
ORDER BY threat_count DESC
LIMIT 100;

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================
