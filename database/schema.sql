-- ============================================================================
-- AI-SOC Database Schema
-- Security Operations Center - Database Design
-- Version: 1.0
-- Date: 2026-08-16
-- ============================================================================

-- Enable UUID extension (PostgreSQL)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- 1. ASSETS TABLE
-- Описание: Инфраструктурные активы (серверы, рабочие станции, устройства)
-- ============================================================================

CREATE TABLE IF NOT EXISTS assets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Основная информация
    asset_name VARCHAR(255) NOT NULL,
    asset_type VARCHAR(50) NOT NULL CHECK (asset_type IN (
        'server', 'workstation', 'network_device', 
        'mobile', 'iot', 'application', 'database'
    )),
    
    -- Сетевые параметры
    ip_address INET,
    mac_address MACADDR,
    hostname VARCHAR(255),
    
    -- Классификация
    criticality VARCHAR(20) DEFAULT 'medium' CHECK (criticality IN (
        'critical', 'high', 'medium', 'low'
    )),
    business_unit VARCHAR(100),
    location VARCHAR(255),
    
    -- Технические параметры
    os_name VARCHAR(100),
    os_version VARCHAR(50),
    last_patch_date TIMESTAMP,
    
    -- Статус
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN (
        'active', 'inactive', 'maintenance', 'compromised', 'isolated'
    )),
    
    -- Владение и ответственность
    owner VARCHAR(100),
    assigned_team VARCHAR(100),
    
    -- Метаданные
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Индексы
    CONSTRAINT unique_asset_identifier UNIQUE (ip_address, mac_address)
);

CREATE INDEX idx_assets_ip ON assets(ip_address);
CREATE INDEX idx_assets_type ON assets(asset_type);
CREATE INDEX idx_assets_status ON assets(status);
CREATE INDEX idx_assets_criticality ON assets(criticality);

-- ============================================================================
-- 2. SECURITY_EVENTS TABLE
-- Описание: События безопасности из различных источников
-- ============================================================================

CREATE TABLE IF NOT EXISTS security_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Временные метки
    event_timestamp TIMESTAMP NOT NULL,
    received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Источник события
    source_system VARCHAR(100) NOT NULL, -- firewall, ids, waf, auth, etc
    source_ip INET,
    source_port INTEGER,
    source_asset_id UUID REFERENCES assets(id),
    
    -- Назначение
    destination_ip INET,
    destination_port INTEGER,
    destination_asset_id UUID REFERENCES assets(id),
    
    -- Классификация события
    event_type VARCHAR(100) NOT NULL, -- login_attempt, port_scan, malware_detected, etc
    event_category VARCHAR(50) NOT NULL CHECK (event_category IN (
        'authentication', 'network', 'malware', 'data_access',
        'system', 'application', 'policy_violation', 'anomaly'
    )),
    
    -- Severity
    severity VARCHAR(20) DEFAULT 'medium' CHECK (severity IN (
        'critical', 'high', 'medium', 'low', 'info'
    )),
    
    -- Детали
    event_description TEXT,
    raw_log TEXT,
    parsed_data JSONB,
    
    -- Пользовательский контекст
    username VARCHAR(255),
    user_agent TEXT,
    
    -- Протокол и действие
    protocol VARCHAR(20), -- TCP, UDP, HTTP, HTTPS, etc
    action_taken VARCHAR(50), -- allowed, blocked, logged
    
    -- Обработка
    processed BOOLEAN DEFAULT FALSE,
    false_positive BOOLEAN DEFAULT FALSE,
    
    -- Метаданные
    tags TEXT[],
    metadata JSONB,
    
    -- Индексы
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_events_timestamp ON security_events(event_timestamp DESC);
CREATE INDEX idx_events_source_ip ON security_events(source_ip);
CREATE INDEX idx_events_dest_ip ON security_events(destination_ip);
CREATE INDEX idx_events_type ON security_events(event_type);
CREATE INDEX idx_events_severity ON security_events(severity);
CREATE INDEX idx_events_processed ON security_events(processed);
CREATE INDEX idx_events_source_asset ON security_events(source_asset_id);

-- ============================================================================
-- 3. INDICATORS_OF_COMPROMISE (IoC) TABLE
-- Описание: Индикаторы компрометации (malicious IPs, domains, hashes)
-- ============================================================================

CREATE TABLE IF NOT EXISTS indicators_of_compromise (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Тип индикатора
    ioc_type VARCHAR(50) NOT NULL CHECK (ioc_type IN (
        'ip_address', 'domain', 'url', 'file_hash', 
        'email', 'registry_key', 'mutex', 'certificate'
    )),
    
    -- Значение индикатора
    ioc_value TEXT NOT NULL,
    hash_type VARCHAR(20), -- MD5, SHA1, SHA256 (для file_hash)
    
    -- Классификация угрозы
    threat_type VARCHAR(100), -- malware, phishing, c2, botnet, etc
    malware_family VARCHAR(100),
    
    -- Severity и confidence
    severity VARCHAR(20) DEFAULT 'medium' CHECK (severity IN (
        'critical', 'high', 'medium', 'low'
    )),
    confidence_score INTEGER CHECK (confidence_score >= 0 AND confidence_score <= 100),
    
    -- Источник данных
    source VARCHAR(100) NOT NULL, -- VirusTotal, AbuseIPDB, internal, etc
    source_url TEXT,
    
    -- Временные рамки
    first_seen TIMESTAMP,
    last_seen TIMESTAMP,
    expires_at TIMESTAMP,
    
    -- Контекст
    description TEXT,
    attack_pattern TEXT, -- MITRE ATT&CK
    
    -- Статус
    is_active BOOLEAN DEFAULT TRUE,
    false_positive BOOLEAN DEFAULT FALSE,
    
    -- Метаданные
    tags TEXT[],
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Уникальность
    CONSTRAINT unique_ioc UNIQUE (ioc_type, ioc_value)
);

CREATE INDEX idx_ioc_type ON indicators_of_compromise(ioc_type);
CREATE INDEX idx_ioc_value ON indicators_of_compromise(ioc_value);
CREATE INDEX idx_ioc_active ON indicators_of_compromise(is_active);
CREATE INDEX idx_ioc_severity ON indicators_of_compromise(severity);
CREATE INDEX idx_ioc_threat_type ON indicators_of_compromise(threat_type);

-- ============================================================================
-- 4. VULNERABILITIES TABLE
-- Описание: Обнаруженные уязвимости (CVE)
-- ============================================================================

CREATE TABLE IF NOT EXISTS vulnerabilities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- CVE информация
    cve_id VARCHAR(50), -- CVE-2021-44228
    cve_published_date DATE,
    
    -- Затронутый актив
    asset_id UUID NOT NULL REFERENCES assets(id) ON DELETE CASCADE,
    
    -- Описание уязвимости
    vulnerability_name VARCHAR(255) NOT NULL,
    description TEXT,
    
    -- Severity (CVSS)
    cvss_score DECIMAL(3,1) CHECK (cvss_score >= 0 AND cvss_score <= 10),
    cvss_vector VARCHAR(100),
    severity VARCHAR(20) CHECK (severity IN (
        'critical', 'high', 'medium', 'low', 'info'
    )),
    
    -- Категория
    vulnerability_type VARCHAR(100), -- RCE, SQLi, XSS, etc
    category VARCHAR(50),
    
    -- Затронутое ПО
    affected_software VARCHAR(255),
    affected_version VARCHAR(100),
    
    -- Эксплойты
    exploit_available BOOLEAN DEFAULT FALSE,
    exploit_public BOOLEAN DEFAULT FALSE,
    actively_exploited BOOLEAN DEFAULT FALSE,
    
    -- Remediation
    patch_available BOOLEAN DEFAULT FALSE,
    patch_version VARCHAR(100),
    remediation_steps TEXT,
    workaround TEXT,
    
    -- Статус
    status VARCHAR(50) DEFAULT 'open' CHECK (status IN (
        'open', 'in_progress', 'patched', 'mitigated', 
        'accepted_risk', 'false_positive', 'closed'
    )),
    
    -- Приоритет и timeline
    priority VARCHAR(20) DEFAULT 'medium' CHECK (priority IN (
        'critical', 'high', 'medium', 'low'
    )),
    due_date DATE,
    
    -- Назначение
    assigned_to VARCHAR(100),
    assigned_team VARCHAR(100),
    
    -- Сканирование
    scan_date TIMESTAMP,
    scanner_name VARCHAR(100),
    
    -- Даты
    discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP,
    verified_at TIMESTAMP,
    
    -- Метаданные
    tags TEXT[],
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_vuln_asset ON vulnerabilities(asset_id);
CREATE INDEX idx_vuln_cve ON vulnerabilities(cve_id);
CREATE INDEX idx_vuln_severity ON vulnerabilities(severity);
CREATE INDEX idx_vuln_status ON vulnerabilities(status);
CREATE INDEX idx_vuln_priority ON vulnerabilities(priority);
CREATE INDEX idx_vuln_cvss ON vulnerabilities(cvss_score DESC);

-- ============================================================================
-- 5. THREATS TABLE
-- Описание: Обнаруженные угрозы (результат анализа событий)
-- ============================================================================

CREATE TABLE IF NOT EXISTS threats (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Связь с событиями
    source_event_ids UUID[], -- массив ID событий, которые привели к угрозе
    primary_event_id UUID REFERENCES security_events(id),
    
    -- Затронутые активы
    affected_asset_ids UUID[], -- массив затронутых активов
    primary_asset_id UUID REFERENCES assets(id),
    
    -- Классификация угрозы
    threat_type VARCHAR(100) NOT NULL, -- brute_force, malware, ddos, data_exfiltration
    threat_category VARCHAR(50) NOT NULL CHECK (threat_category IN (
        'intrusion', 'malware', 'dos_ddos', 'data_breach',
        'insider_threat', 'phishing', 'exploit', 'anomaly'
    )),
    threat_name VARCHAR(255),
    
    -- Детекция
    detection_method VARCHAR(50) CHECK (detection_method IN (
        'signature', 'anomaly', 'behavioral', 'ml_model', 'manual'
    )),
    detection_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Severity и confidence
    severity VARCHAR(20) DEFAULT 'medium' CHECK (severity IN (
        'critical', 'high', 'medium', 'low'
    )),
    confidence_score INTEGER CHECK (confidence_score >= 0 AND confidence_score <= 100),
    risk_score INTEGER CHECK (risk_score >= 0 AND risk_score <= 100),
    
    -- Источник угрозы
    source_ip INET,
    source_country VARCHAR(2), -- ISO код
    source_geolocation POINT,
    
    -- Целевые параметры
    target_ip INET,
    target_port INTEGER,
    attack_vector VARCHAR(100),
    
    -- MITRE ATT&CK
    mitre_tactic VARCHAR(100), -- Initial Access, Execution, etc
    mitre_technique VARCHAR(100), -- T1078, T1190, etc
    mitre_subtechnique VARCHAR(100),
    
    -- Описание
    description TEXT,
    technical_details TEXT,
    indicators JSONB, -- связанные IoC
    
    -- Статус
    status VARCHAR(50) DEFAULT 'active' CHECK (status IN (
        'active', 'investigating', 'contained', 
        'resolved', 'false_positive', 'monitoring'
    )),
    
    -- Временная линия
    first_detected_at TIMESTAMP,
    last_detected_at TIMESTAMP,
    resolved_at TIMESTAMP,
    
    -- False positive
    false_positive BOOLEAN DEFAULT FALSE,
    false_positive_reason TEXT,
    
    -- Метаданные
    tags TEXT[],
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_threats_status ON threats(status);
CREATE INDEX idx_threats_severity ON threats(severity);
CREATE INDEX idx_threats_type ON threats(threat_type);
CREATE INDEX idx_threats_detection ON threats(detection_timestamp DESC);
CREATE INDEX idx_threats_source_ip ON threats(source_ip);
CREATE INDEX idx_threats_asset ON threats(primary_asset_id);
CREATE INDEX idx_threats_mitre ON threats(mitre_technique);

-- ============================================================================
-- 6. INCIDENTS TABLE
-- Описание: Инциденты безопасности (формализованные угрозы)
-- ============================================================================

CREATE TABLE IF NOT EXISTS incidents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Идентификация
    incident_number VARCHAR(50) UNIQUE NOT NULL, -- INC-2024-001
    incident_title VARCHAR(255) NOT NULL,
    
    -- Связанные угрозы и события
    threat_ids UUID[], -- связанные угрозы
    primary_threat_id UUID REFERENCES threats(id),
    event_count INTEGER DEFAULT 0,
    
    -- Классификация
    incident_type VARCHAR(100) NOT NULL,
    incident_category VARCHAR(50) CHECK (incident_category IN (
        'security_breach', 'data_loss', 'service_disruption',
        'policy_violation', 'malware_infection', 'unauthorized_access'
    )),
    
    -- Severity и impact
    severity VARCHAR(20) DEFAULT 'medium' CHECK (severity IN (
        'critical', 'high', 'medium', 'low'
    )),
    impact VARCHAR(50) CHECK (impact IN (
        'critical', 'high', 'medium', 'low', 'none'
    )),
    urgency VARCHAR(50) CHECK (urgency IN (
        'critical', 'high', 'medium', 'low'
    )),
    
    -- Scope
    affected_asset_ids UUID[],
    affected_users TEXT[],
    affected_systems_count INTEGER DEFAULT 0,
    
    -- Описание
    description TEXT NOT NULL,
    attack_narrative TEXT,
    business_impact TEXT,
    
    -- Статус и workflow
    status VARCHAR(50) DEFAULT 'new' CHECK (status IN (
        'new', 'assigned', 'investigating', 'containing',
        'eradicating', 'recovering', 'resolved', 'closed'
    )),
    
    -- Назначение
    assigned_to VARCHAR(100),
    assigned_team VARCHAR(100),
    escalation_level INTEGER DEFAULT 1 CHECK (escalation_level BETWEEN 1 AND 3),
    
    -- SLA и timeline
    reported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    acknowledged_at TIMESTAMP,
    started_at TIMESTAMP,
    contained_at TIMESTAMP,
    resolved_at TIMESTAMP,
    closed_at TIMESTAMP,
    
    -- SLA compliance
    sla_deadline TIMESTAMP,
    sla_breached BOOLEAN DEFAULT FALSE,
    
    -- Root cause
    root_cause TEXT,
    lessons_learned TEXT,
    
    -- Метаданные
    tags TEXT[],
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_incidents_number ON incidents(incident_number);
CREATE INDEX idx_incidents_status ON incidents(status);
CREATE INDEX idx_incidents_severity ON incidents(severity);
CREATE INDEX idx_incidents_reported ON incidents(reported_at DESC);
CREATE INDEX idx_incidents_assigned ON incidents(assigned_to);
CREATE INDEX idx_incidents_threat ON incidents(primary_threat_id);

-- ============================================================================
-- 7. RESPONSE_ACTIONS TABLE
-- Описание: Действия по реагированию на инциденты
-- ============================================================================

CREATE TABLE IF NOT EXISTS response_actions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Связь с инцидентом
    incident_id UUID NOT NULL REFERENCES incidents(id) ON DELETE CASCADE,
    threat_id UUID REFERENCES threats(id),
    
    -- Тип действия
    action_type VARCHAR(50) NOT NULL CHECK (action_type IN (
        'block_ip', 'isolate_host', 'disable_account', 
        'kill_process', 'quarantine_file', 'update_firewall',
        'reset_password', 'revoke_access', 'backup_data',
        'collect_evidence', 'notify', 'escalate', 'manual_intervention'
    )),
    action_category VARCHAR(50) CHECK (action_category IN (
        'containment', 'eradication', 'recovery', 'investigation', 'notification'
    )),
    
    -- Описание действия
    action_description TEXT NOT NULL,
    action_details JSONB,
    
    -- Целевые объекты
    target_asset_id UUID REFERENCES assets(id),
    target_ip INET,
    target_user VARCHAR(255),
    target_identifiers JSONB, -- гибкое хранение целей
    
    -- Статус выполнения
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN (
        'pending', 'in_progress', 'completed', 'failed', 'rolled_back', 'cancelled'
    )),
    
    -- Автоматизация
    automated BOOLEAN DEFAULT FALSE,
    auto_approved BOOLEAN DEFAULT FALSE,
    requires_approval BOOLEAN DEFAULT FALSE,
    approved_by VARCHAR(100),
    approved_at TIMESTAMP,
    
    -- Исполнение
    executed_by VARCHAR(100), -- user or system
    execution_method VARCHAR(50), -- api, ssh, manual, script
    
    -- Результат
    result TEXT,
    success BOOLEAN,
    error_message TEXT,
    
    -- Временные метки
    scheduled_at TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    
    -- Rollback
    rollback_possible BOOLEAN DEFAULT FALSE,
    rollback_action_id UUID REFERENCES response_actions(id),
    
    -- Метаданные
    tags TEXT[],
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_actions_incident ON response_actions(incident_id);
CREATE INDEX idx_actions_threat ON response_actions(threat_id);
CREATE INDEX idx_actions_type ON response_actions(action_type);
CREATE INDEX idx_actions_status ON response_actions(status);
CREATE INDEX idx_actions_asset ON response_actions(target_asset_id);
CREATE INDEX idx_actions_executed ON response_actions(completed_at DESC);

-- ============================================================================
-- TRIGGERS для updated_at
-- ============================================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_assets_updated_at BEFORE UPDATE ON assets
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_ioc_updated_at BEFORE UPDATE ON indicators_of_compromise
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_vulnerabilities_updated_at BEFORE UPDATE ON vulnerabilities
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_threats_updated_at BEFORE UPDATE ON threats
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_incidents_updated_at BEFORE UPDATE ON incidents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_response_actions_updated_at BEFORE UPDATE ON response_actions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- VIEWS для аналитики
-- ============================================================================

-- View: Активные критические угрозы
CREATE OR REPLACE VIEW active_critical_threats AS
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

-- View: Статистика инцидентов по дням
CREATE OR REPLACE VIEW incidents_daily_stats AS
SELECT 
    DATE(reported_at) as incident_date,
    COUNT(*) as total_incidents,
    COUNT(*) FILTER (WHERE severity = 'critical') as critical_count,
    COUNT(*) FILTER (WHERE severity = 'high') as high_count,
    COUNT(*) FILTER (WHERE status = 'resolved') as resolved_count,
    AVG(EXTRACT(EPOCH FROM (resolved_at - reported_at))/3600) as avg_resolution_hours
FROM incidents
GROUP BY DATE(reported_at)
ORDER BY incident_date DESC;

-- View: Top атакующие IP
CREATE OR REPLACE VIEW top_attacking_ips AS
SELECT 
    source_ip,
    COUNT(*) as threat_count,
    MAX(severity) as max_severity,
    MIN(first_detected_at) as first_seen,
    MAX(last_detected_at) as last_seen,
    ARRAY_AGG(DISTINCT threat_type) as threat_types
FROM threats
WHERE source_ip IS NOT NULL
GROUP BY source_ip
ORDER BY threat_count DESC
LIMIT 100;

-- ============================================================================
-- Комментарии к таблицам
-- ============================================================================

COMMENT ON TABLE assets IS 'Инфраструктурные активы организации';
COMMENT ON TABLE security_events IS 'События безопасности из различных источников';
COMMENT ON TABLE indicators_of_compromise IS 'Индикаторы компрометации (IoC)';
COMMENT ON TABLE vulnerabilities IS 'Обнаруженные уязвимости';
COMMENT ON TABLE threats IS 'Детектированные угрозы';
COMMENT ON TABLE incidents IS 'Инциденты безопасности';
COMMENT ON TABLE response_actions IS 'Действия по реагированию на инциденты';

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================
