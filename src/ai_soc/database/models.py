"""
SQLAlchemy ORM Models
Модели для всех таблиц AI-SOC базы данных
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    Column, Integer, String, Text, Float, Boolean,
    DateTime, ForeignKey, JSON, CheckConstraint
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from .connection import Base


class Asset(Base):
    """Инфраструктурные активы"""
    __tablename__ = 'assets'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Основная информация
    asset_name: Mapped[str] = mapped_column(String(255), nullable=False)
    asset_type: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # Сетевые параметры
    ip_address: Mapped[Optional[str]] = mapped_column(String(45))
    mac_address: Mapped[Optional[str]] = mapped_column(String(17))
    hostname: Mapped[Optional[str]] = mapped_column(String(255))
    
    # Классификация
    criticality: Mapped[str] = mapped_column(String(20), default='medium')
    business_unit: Mapped[Optional[str]] = mapped_column(String(100))
    location: Mapped[Optional[str]] = mapped_column(String(255))
    
    # Технические параметры
    os_name: Mapped[Optional[str]] = mapped_column(String(100))
    os_version: Mapped[Optional[str]] = mapped_column(String(50))
    last_patch_date: Mapped[Optional[str]] = mapped_column(String(10))
    
    # Статус
    status: Mapped[str] = mapped_column(String(20), default='active')
    
    # Владение
    owner: Mapped[Optional[str]] = mapped_column(String(100))
    assigned_team: Mapped[Optional[str]] = mapped_column(String(100))
    
    # Метаданные
    meta_data: Mapped[Optional[str]] = mapped_column('metadata', Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    vulnerabilities: Mapped[List["Vulnerability"]] = relationship("Vulnerability", back_populates="asset")
    
    def __repr__(self):
        return f"<Asset(id={self.id}, name='{self.asset_name}', type='{self.asset_type}')>"


class SecurityEvent(Base):
    """События безопасности"""
    __tablename__ = 'security_events'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Временные метки
    event_timestamp: Mapped[str] = mapped_column(String(30), nullable=False)
    received_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    
    # Источник события
    source_system: Mapped[str] = mapped_column(String(100), nullable=False)
    source_ip: Mapped[Optional[str]] = mapped_column(String(45))
    source_port: Mapped[Optional[int]] = mapped_column(Integer)
    source_asset_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('assets.id'))
    
    # Назначение
    destination_ip: Mapped[Optional[str]] = mapped_column(String(45))
    destination_port: Mapped[Optional[int]] = mapped_column(Integer)
    destination_asset_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('assets.id'))
    
    # Классификация события
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    event_category: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # Severity
    severity: Mapped[str] = mapped_column(String(20), default='medium')
    
    # Детали
    event_description: Mapped[Optional[str]] = mapped_column(Text)
    raw_log: Mapped[Optional[str]] = mapped_column(Text)
    parsed_data: Mapped[Optional[str]] = mapped_column(Text)
    
    # Пользовательский контекст
    username: Mapped[Optional[str]] = mapped_column(String(255))
    user_agent: Mapped[Optional[str]] = mapped_column(Text)
    
    # Протокол и действие
    protocol: Mapped[Optional[str]] = mapped_column(String(20))
    action_taken: Mapped[Optional[str]] = mapped_column(String(50))
    
    # Обработка
    processed: Mapped[bool] = mapped_column(Boolean, default=False)
    false_positive: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Метаданные
    tags: Mapped[Optional[str]] = mapped_column(Text)
    meta_data: Mapped[Optional[str]] = mapped_column("metadata", Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    
    def __repr__(self):
        return f"<SecurityEvent(id={self.id}, type='{self.event_type}', severity='{self.severity}')>"


class IndicatorOfCompromise(Base):
    """Индикаторы компрометации (IoC)"""
    __tablename__ = 'indicators_of_compromise'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Тип индикатора
    ioc_type: Mapped[str] = mapped_column(String(50), nullable=False)
    ioc_value: Mapped[str] = mapped_column(Text, nullable=False)
    hash_type: Mapped[Optional[str]] = mapped_column(String(20))
    
    # Классификация угрозы
    threat_type: Mapped[Optional[str]] = mapped_column(String(100))
    malware_family: Mapped[Optional[str]] = mapped_column(String(100))
    
    # Severity и confidence
    severity: Mapped[str] = mapped_column(String(20), default='medium')
    confidence_score: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Источник данных
    source: Mapped[str] = mapped_column(String(100), nullable=False)
    source_url: Mapped[Optional[str]] = mapped_column(Text)
    
    # Временные рамки
    first_seen: Mapped[Optional[str]] = mapped_column(String(10))
    last_seen: Mapped[Optional[str]] = mapped_column(String(10))
    expires_at: Mapped[Optional[str]] = mapped_column(String(10))
    
    # Контекст
    description: Mapped[Optional[str]] = mapped_column(Text)
    attack_pattern: Mapped[Optional[str]] = mapped_column(Text)
    
    # Статус
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    false_positive: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Метаданные
    tags: Mapped[Optional[str]] = mapped_column(Text)
    meta_data: Mapped[Optional[str]] = mapped_column("metadata", Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    def __repr__(self):
        return f"<IoC(id={self.id}, type='{self.ioc_type}', value='{self.ioc_value[:20]}...')>"


class Vulnerability(Base):
    """Обнаруженные уязвимости"""
    __tablename__ = 'vulnerabilities'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # CVE информация
    cve_id: Mapped[Optional[str]] = mapped_column(String(50))
    cve_published_date: Mapped[Optional[str]] = mapped_column(String(10))
    
    # Затронутый актив
    asset_id: Mapped[int] = mapped_column(Integer, ForeignKey('assets.id'), nullable=False)
    
    # Описание уязвимости
    vulnerability_name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    
    # Severity (CVSS)
    cvss_score: Mapped[Optional[float]] = mapped_column(Float)
    cvss_vector: Mapped[Optional[str]] = mapped_column(String(100))
    severity: Mapped[Optional[str]] = mapped_column(String(20))
    
    # Категория
    vulnerability_type: Mapped[Optional[str]] = mapped_column(String(100))
    category: Mapped[Optional[str]] = mapped_column(String(50))
    
    # Затронутое ПО
    affected_software: Mapped[Optional[str]] = mapped_column(String(255))
    affected_version: Mapped[Optional[str]] = mapped_column(String(100))
    
    # Эксплойты
    exploit_available: Mapped[bool] = mapped_column(Boolean, default=False)
    exploit_public: Mapped[bool] = mapped_column(Boolean, default=False)
    actively_exploited: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Remediation
    patch_available: Mapped[bool] = mapped_column(Boolean, default=False)
    patch_version: Mapped[Optional[str]] = mapped_column(String(100))
    remediation_steps: Mapped[Optional[str]] = mapped_column(Text)
    workaround: Mapped[Optional[str]] = mapped_column(Text)
    
    # Статус
    status: Mapped[str] = mapped_column(String(50), default='open')
    
    # Приоритет и timeline
    priority: Mapped[str] = mapped_column(String(20), default='medium')
    due_date: Mapped[Optional[str]] = mapped_column(String(10))
    
    # Назначение
    assigned_to: Mapped[Optional[str]] = mapped_column(String(100))
    assigned_team: Mapped[Optional[str]] = mapped_column(String(100))
    
    # Сканирование
    scan_date: Mapped[Optional[str]] = mapped_column(String(30))
    scanner_name: Mapped[Optional[str]] = mapped_column(String(100))
    
    # Даты
    discovered_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # Метаданные
    tags: Mapped[Optional[str]] = mapped_column(Text)
    meta_data: Mapped[Optional[str]] = mapped_column("metadata", Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    asset: Mapped["Asset"] = relationship("Asset", back_populates="vulnerabilities")
    
    def __repr__(self):
        return f"<Vulnerability(id={self.id}, cve='{self.cve_id}', severity='{self.severity}')>"


class Threat(Base):
    """Обнаруженные угрозы"""
    __tablename__ = 'threats'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Связь с событиями
    source_event_ids: Mapped[Optional[str]] = mapped_column(Text)
    primary_event_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('security_events.id'))
    
    # Затронутые активы
    affected_asset_ids: Mapped[Optional[str]] = mapped_column(Text)
    primary_asset_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('assets.id'))
    
    # Классификация угрозы
    threat_type: Mapped[str] = mapped_column(String(100), nullable=False)
    threat_category: Mapped[str] = mapped_column(String(50), nullable=False)
    threat_name: Mapped[Optional[str]] = mapped_column(String(255))
    
    # Детекция
    detection_method: Mapped[Optional[str]] = mapped_column(String(50))
    detection_timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    
    # Severity и confidence
    severity: Mapped[str] = mapped_column(String(20), default='medium')
    confidence_score: Mapped[Optional[int]] = mapped_column(Integer)
    risk_score: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Источник угрозы
    source_ip: Mapped[Optional[str]] = mapped_column(String(45))
    source_country: Mapped[Optional[str]] = mapped_column(String(2))
    source_geolocation: Mapped[Optional[str]] = mapped_column(String(100))
    
    # Целевые параметры
    target_ip: Mapped[Optional[str]] = mapped_column(String(45))
    target_port: Mapped[Optional[int]] = mapped_column(Integer)
    attack_vector: Mapped[Optional[str]] = mapped_column(String(100))
    
    # MITRE ATT&CK
    mitre_tactic: Mapped[Optional[str]] = mapped_column(String(100))
    mitre_technique: Mapped[Optional[str]] = mapped_column(String(100))
    mitre_subtechnique: Mapped[Optional[str]] = mapped_column(String(100))
    
    # Описание
    description: Mapped[Optional[str]] = mapped_column(Text)
    technical_details: Mapped[Optional[str]] = mapped_column(Text)
    indicators: Mapped[Optional[str]] = mapped_column(Text)
    
    # Статус
    status: Mapped[str] = mapped_column(String(50), default='active')
    
    # Временная линия
    first_detected_at: Mapped[Optional[str]] = mapped_column(String(30))
    last_detected_at: Mapped[Optional[str]] = mapped_column(String(30))
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # False positive
    false_positive: Mapped[bool] = mapped_column(Boolean, default=False)
    false_positive_reason: Mapped[Optional[str]] = mapped_column(Text)
    
    # Метаданные
    tags: Mapped[Optional[str]] = mapped_column(Text)
    meta_data: Mapped[Optional[str]] = mapped_column("metadata", Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    incidents: Mapped[List["Incident"]] = relationship("Incident", back_populates="primary_threat")
    
    def __repr__(self):
        return f"<Threat(id={self.id}, type='{self.threat_type}', severity='{self.severity}')>"


class Incident(Base):
    """Инциденты безопасности"""
    __tablename__ = 'incidents'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Идентификация
    incident_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    incident_title: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Связанные угрозы и события
    threat_ids: Mapped[Optional[str]] = mapped_column(Text)
    primary_threat_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('threats.id'))
    event_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Классификация
    incident_type: Mapped[str] = mapped_column(String(100), nullable=False)
    incident_category: Mapped[Optional[str]] = mapped_column(String(50))
    
    # Severity и impact
    severity: Mapped[str] = mapped_column(String(20), default='medium')
    impact: Mapped[Optional[str]] = mapped_column(String(50))
    urgency: Mapped[Optional[str]] = mapped_column(String(50))
    
    # Scope
    affected_asset_ids: Mapped[Optional[str]] = mapped_column(Text)
    affected_users: Mapped[Optional[str]] = mapped_column(Text)
    affected_systems_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Описание
    description: Mapped[str] = mapped_column(Text, nullable=False)
    attack_narrative: Mapped[Optional[str]] = mapped_column(Text)
    business_impact: Mapped[Optional[str]] = mapped_column(Text)
    
    # Статус и workflow
    status: Mapped[str] = mapped_column(String(50), default='new')
    
    # Назначение
    assigned_to: Mapped[Optional[str]] = mapped_column(String(100))
    assigned_team: Mapped[Optional[str]] = mapped_column(String(100))
    escalation_level: Mapped[int] = mapped_column(Integer, default=1)
    
    # SLA и timeline
    reported_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    acknowledged_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    contained_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    closed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # SLA compliance
    sla_deadline: Mapped[Optional[str]] = mapped_column(String(30))
    sla_breached: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Root cause
    root_cause: Mapped[Optional[str]] = mapped_column(Text)
    lessons_learned: Mapped[Optional[str]] = mapped_column(Text)
    
    # Метаданные
    tags: Mapped[Optional[str]] = mapped_column(Text)
    meta_data: Mapped[Optional[str]] = mapped_column("metadata", Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    primary_threat: Mapped[Optional["Threat"]] = relationship("Threat", back_populates="incidents")
    response_actions: Mapped[List["ResponseAction"]] = relationship("ResponseAction", back_populates="incident")
    
    def __repr__(self):
        return f"<Incident(id={self.id}, number='{self.incident_number}', status='{self.status}')>"


class ResponseAction(Base):
    """Действия по реагированию на инциденты"""
    __tablename__ = 'response_actions'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Связь с инцидентом
    incident_id: Mapped[int] = mapped_column(Integer, ForeignKey('incidents.id'), nullable=False)
    threat_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('threats.id'))
    
    # Тип действия
    action_type: Mapped[str] = mapped_column(String(50), nullable=False)
    action_category: Mapped[Optional[str]] = mapped_column(String(50))
    
    # Описание действия
    action_description: Mapped[str] = mapped_column(Text, nullable=False)
    action_details: Mapped[Optional[str]] = mapped_column(Text)
    
    # Целевые объекты
    target_asset_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('assets.id'))
    target_ip: Mapped[Optional[str]] = mapped_column(String(45))
    target_user: Mapped[Optional[str]] = mapped_column(String(255))
    target_identifiers: Mapped[Optional[str]] = mapped_column(Text)
    
    # Статус выполнения
    status: Mapped[str] = mapped_column(String(50), default='pending')
    
    # Автоматизация
    automated: Mapped[bool] = mapped_column(Boolean, default=False)
    auto_approved: Mapped[bool] = mapped_column(Boolean, default=False)
    requires_approval: Mapped[bool] = mapped_column(Boolean, default=False)
    approved_by: Mapped[Optional[str]] = mapped_column(String(100))
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # Исполнение
    executed_by: Mapped[Optional[str]] = mapped_column(String(100))
    execution_method: Mapped[Optional[str]] = mapped_column(String(50))
    
    # Результат
    result: Mapped[Optional[str]] = mapped_column(Text)
    success: Mapped[Optional[bool]] = mapped_column(Boolean)
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    
    # Временные метки
    scheduled_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # Rollback
    rollback_possible: Mapped[bool] = mapped_column(Boolean, default=False)
    rollback_action_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('response_actions.id'))
    
    # Метаданные
    tags: Mapped[Optional[str]] = mapped_column(Text)
    meta_data: Mapped[Optional[str]] = mapped_column("metadata", Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    incident: Mapped["Incident"] = relationship("Incident", back_populates="response_actions")
    
    def __repr__(self):
        return f"<ResponseAction(id={self.id}, type='{self.action_type}', status='{self.status}')>"
