"""
Repository Pattern для работы с базой данных
CRUD операции для всех моделей
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc
from datetime import datetime

from .models import (
    Asset, SecurityEvent, IndicatorOfCompromise,
    Vulnerability, Threat, Incident, ResponseAction
)


class BaseRepository:
    """Базовый класс для всех repositories"""
    
    def __init__(self, session: Session, model):
        self.session = session
        self.model = model
    
    def get_by_id(self, id: int) -> Optional[Any]:
        """Получить запись по ID"""
        return self.session.query(self.model).filter(self.model.id == id).first()
    
    def get_all(self, limit: int = 100, offset: int = 0) -> List[Any]:
        """Получить все записи"""
        return self.session.query(self.model).limit(limit).offset(offset).all()
    
    def create(self, **kwargs) -> Any:
        """Создать новую запись"""
        obj = self.model(**kwargs)
        self.session.add(obj)
        self.session.flush()
        return obj
    
    def update(self, id: int, **kwargs) -> Optional[Any]:
        """Обновить запись"""
        obj = self.get_by_id(id)
        if obj:
            for key, value in kwargs.items():
                if hasattr(obj, key):
                    setattr(obj, key, value)
            self.session.flush()
        return obj
    
    def delete(self, id: int) -> bool:
        """Удалить запись"""
        obj = self.get_by_id(id)
        if obj:
            self.session.delete(obj)
            self.session.flush()
            return True
        return False
    
    def count(self) -> int:
        """Подсчитать количество записей"""
        return self.session.query(self.model).count()


class AssetRepository(BaseRepository):
    """Repository для Assets"""
    
    def __init__(self, session: Session):
        super().__init__(session, Asset)
    
    def get_by_ip(self, ip_address: str) -> Optional[Asset]:
        """Получить asset по IP адресу"""
        return self.session.query(Asset).filter(Asset.ip_address == ip_address).first()
    
    def get_by_type(self, asset_type: str) -> List[Asset]:
        """Получить assets по типу"""
        return self.session.query(Asset).filter(Asset.asset_type == asset_type).all()
    
    def get_by_criticality(self, criticality: str) -> List[Asset]:
        """Получить assets по критичности"""
        return self.session.query(Asset).filter(Asset.criticality == criticality).all()
    
    def get_by_status(self, status: str) -> List[Asset]:
        """Получить assets по статусу"""
        return self.session.query(Asset).filter(Asset.status == status).all()
    
    def get_critical_assets(self) -> List[Asset]:
        """Получить критичные assets"""
        return self.session.query(Asset).filter(
            Asset.criticality.in_(['critical', 'high'])
        ).all()
    
    def get_compromised_assets(self) -> List[Asset]:
        """Получить скомпрометированные assets"""
        return self.session.query(Asset).filter(Asset.status == 'compromised').all()
    
    def search(self, query: str) -> List[Asset]:
        """Поиск assets по имени, IP или hostname"""
        search_pattern = f"%{query}%"
        return self.session.query(Asset).filter(
            or_(
                Asset.asset_name.like(search_pattern),
                Asset.ip_address.like(search_pattern),
                Asset.hostname.like(search_pattern)
            )
        ).all()


class SecurityEventRepository(BaseRepository):
    """Repository для Security Events"""
    
    def __init__(self, session: Session):
        super().__init__(session, SecurityEvent)
    
    def get_by_severity(self, severity: str, limit: int = 100) -> List[SecurityEvent]:
        """Получить события по severity"""
        return self.session.query(SecurityEvent).filter(
            SecurityEvent.severity == severity
        ).order_by(desc(SecurityEvent.event_timestamp)).limit(limit).all()
    
    def get_by_source_ip(self, source_ip: str) -> List[SecurityEvent]:
        """Получить события от конкретного IP"""
        return self.session.query(SecurityEvent).filter(
            SecurityEvent.source_ip == source_ip
        ).order_by(desc(SecurityEvent.event_timestamp)).all()
    
    def get_by_event_type(self, event_type: str, limit: int = 100) -> List[SecurityEvent]:
        """Получить события по типу"""
        return self.session.query(SecurityEvent).filter(
            SecurityEvent.event_type == event_type
        ).order_by(desc(SecurityEvent.event_timestamp)).limit(limit).all()
    
    def get_unprocessed(self, limit: int = 100) -> List[SecurityEvent]:
        """Получить необработанные события"""
        return self.session.query(SecurityEvent).filter(
            SecurityEvent.processed == False
        ).order_by(asc(SecurityEvent.event_timestamp)).limit(limit).all()
    
    def get_critical_events(self, limit: int = 100) -> List[SecurityEvent]:
        """Получить критичные события"""
        return self.session.query(SecurityEvent).filter(
            SecurityEvent.severity.in_(['critical', 'high'])
        ).order_by(desc(SecurityEvent.event_timestamp)).limit(limit).all()
    
    def get_recent(self, hours: int = 24, limit: int = 100) -> List[SecurityEvent]:
        """Получить последние события за N часов"""
        # Для SQLite используем строковое сравнение
        cutoff = datetime.now().replace(hour=datetime.now().hour - hours)
        return self.session.query(SecurityEvent).filter(
            SecurityEvent.received_at >= cutoff
        ).order_by(desc(SecurityEvent.event_timestamp)).limit(limit).all()
    
    def mark_as_processed(self, event_id: int) -> bool:
        """Отметить событие как обработанное"""
        event = self.get_by_id(event_id)
        if event:
            event.processed = True
            self.session.flush()
            return True
        return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Получить статистику по событиям"""
        total = self.count()
        
        # По severity
        critical = self.session.query(SecurityEvent).filter(
            SecurityEvent.severity == 'critical'
        ).count()
        high = self.session.query(SecurityEvent).filter(
            SecurityEvent.severity == 'high'
        ).count()
        
        # По категориям
        categories = {}
        for cat in ['authentication', 'network', 'malware', 'application']:
            categories[cat] = self.session.query(SecurityEvent).filter(
                SecurityEvent.event_category == cat
            ).count()
        
        return {
            'total': total,
            'critical': critical,
            'high': high,
            'by_category': categories
        }


class IoC_Repository(BaseRepository):
    """Repository для Indicators of Compromise"""
    
    def __init__(self, session: Session):
        super().__init__(session, IndicatorOfCompromise)
    
    def get_by_type(self, ioc_type: str) -> List[IndicatorOfCompromise]:
        """Получить IoC по типу"""
        return self.session.query(IndicatorOfCompromise).filter(
            IndicatorOfCompromise.ioc_type == ioc_type
        ).all()
    
    def get_by_value(self, ioc_value: str) -> Optional[IndicatorOfCompromise]:
        """Получить IoC по значению"""
        return self.session.query(IndicatorOfCompromise).filter(
            IndicatorOfCompromise.ioc_value == ioc_value
        ).first()
    
    def get_active(self) -> List[IndicatorOfCompromise]:
        """Получить активные IoC"""
        return self.session.query(IndicatorOfCompromise).filter(
            IndicatorOfCompromise.is_active == True
        ).all()
    
    def get_by_threat_type(self, threat_type: str) -> List[IndicatorOfCompromise]:
        """Получить IoC по типу угрозы"""
        return self.session.query(IndicatorOfCompromise).filter(
            IndicatorOfCompromise.threat_type == threat_type
        ).all()
    
    def get_malicious_ips(self) -> List[IndicatorOfCompromise]:
        """Получить все malicious IP адреса"""
        return self.session.query(IndicatorOfCompromise).filter(
            and_(
                IndicatorOfCompromise.ioc_type == 'ip_address',
                IndicatorOfCompromise.is_active == True
            )
        ).all()
    
    def check_ip(self, ip_address: str) -> Optional[IndicatorOfCompromise]:
        """Проверить IP адрес в IoC"""
        return self.session.query(IndicatorOfCompromise).filter(
            and_(
                IndicatorOfCompromise.ioc_type == 'ip_address',
                IndicatorOfCompromise.ioc_value == ip_address,
                IndicatorOfCompromise.is_active == True
            )
        ).first()
    
    def check_domain(self, domain: str) -> Optional[IndicatorOfCompromise]:
        """Проверить domain в IoC"""
        return self.session.query(IndicatorOfCompromise).filter(
            and_(
                IndicatorOfCompromise.ioc_type == 'domain',
                IndicatorOfCompromise.ioc_value == domain,
                IndicatorOfCompromise.is_active == True
            )
        ).first()
    
    def check_hash(self, file_hash: str) -> Optional[IndicatorOfCompromise]:
        """Проверить file hash в IoC"""
        return self.session.query(IndicatorOfCompromise).filter(
            and_(
                IndicatorOfCompromise.ioc_type == 'file_hash',
                IndicatorOfCompromise.ioc_value == file_hash,
                IndicatorOfCompromise.is_active == True
            )
        ).first()


class VulnerabilityRepository(BaseRepository):
    """Repository для Vulnerabilities"""
    
    def __init__(self, session: Session):
        super().__init__(session, Vulnerability)
    
    def get_by_asset(self, asset_id: int) -> List[Vulnerability]:
        """Получить уязвимости по asset"""
        return self.session.query(Vulnerability).filter(
            Vulnerability.asset_id == asset_id
        ).all()
    
    def get_by_cve(self, cve_id: str) -> List[Vulnerability]:
        """Получить уязвимости по CVE ID"""
        return self.session.query(Vulnerability).filter(
            Vulnerability.cve_id == cve_id
        ).all()
    
    def get_by_severity(self, severity: str) -> List[Vulnerability]:
        """Получить уязвимости по severity"""
        return self.session.query(Vulnerability).filter(
            Vulnerability.severity == severity
        ).all()
    
    def get_open(self) -> List[Vulnerability]:
        """Получить открытые уязвимости"""
        return self.session.query(Vulnerability).filter(
            Vulnerability.status == 'open'
        ).all()
    
    def get_critical(self) -> List[Vulnerability]:
        """Получить критичные уязвимости"""
        return self.session.query(Vulnerability).filter(
            Vulnerability.severity == 'critical'
        ).order_by(desc(Vulnerability.cvss_score)).all()
    
    def get_with_public_exploit(self) -> List[Vulnerability]:
        """Получить уязвимости с public exploit"""
        return self.session.query(Vulnerability).filter(
            Vulnerability.exploit_public == True
        ).all()
    
    def get_actively_exploited(self) -> List[Vulnerability]:
        """Получить активно эксплуатируемые уязвимости"""
        return self.session.query(Vulnerability).filter(
            Vulnerability.actively_exploited == True
        ).all()
    
    def get_overdue(self) -> List[Vulnerability]:
        """Получить просроченные уязвимости"""
        today = datetime.now().strftime('%Y-%m-%d')
        return self.session.query(Vulnerability).filter(
            and_(
                Vulnerability.due_date < today,
                Vulnerability.status == 'open'
            )
        ).all()


class ThreatRepository(BaseRepository):
    """Repository для Threats"""
    
    def __init__(self, session: Session):
        super().__init__(session, Threat)
    
    def get_active(self) -> List[Threat]:
        """Получить активные угрозы"""
        return self.session.query(Threat).filter(
            Threat.status == 'active'
        ).order_by(desc(Threat.detection_timestamp)).all()
    
    def get_by_severity(self, severity: str) -> List[Threat]:
        """Получить угрозы по severity"""
        return self.session.query(Threat).filter(
            Threat.severity == severity
        ).order_by(desc(Threat.detection_timestamp)).all()
    
    def get_by_type(self, threat_type: str) -> List[Threat]:
        """Получить угрозы по типу"""
        return self.session.query(Threat).filter(
            Threat.threat_type == threat_type
        ).all()
    
    def get_by_source_ip(self, source_ip: str) -> List[Threat]:
        """Получить угрозы от конкретного IP"""
        return self.session.query(Threat).filter(
            Threat.source_ip == source_ip
        ).all()
    
    def get_critical_active(self) -> List[Threat]:
        """Получить критичные активные угрозы"""
        return self.session.query(Threat).filter(
            and_(
                Threat.status == 'active',
                Threat.severity.in_(['critical', 'high'])
            )
        ).order_by(desc(Threat.detection_timestamp)).all()
    
    def get_recent(self, hours: int = 24) -> List[Threat]:
        """Получить недавние угрозы"""
        cutoff = datetime.now().replace(hour=datetime.now().hour - hours)
        return self.session.query(Threat).filter(
            Threat.detection_timestamp >= cutoff
        ).order_by(desc(Threat.detection_timestamp)).all()


class IncidentRepository(BaseRepository):
    """Repository для Incidents"""
    
    def __init__(self, session: Session):
        super().__init__(session, Incident)
    
    def get_by_number(self, incident_number: str) -> Optional[Incident]:
        """Получить инцидент по номеру"""
        return self.session.query(Incident).filter(
            Incident.incident_number == incident_number
        ).first()
    
    def get_open(self) -> List[Incident]:
        """Получить открытые инциденты"""
        return self.session.query(Incident).filter(
            Incident.status.in_(['new', 'assigned', 'investigating'])
        ).order_by(desc(Incident.reported_at)).all()
    
    def get_by_status(self, status: str) -> List[Incident]:
        """Получить инциденты по статусу"""
        return self.session.query(Incident).filter(
            Incident.status == status
        ).order_by(desc(Incident.reported_at)).all()
    
    def get_by_severity(self, severity: str) -> List[Incident]:
        """Получить инциденты по severity"""
        return self.session.query(Incident).filter(
            Incident.severity == severity
        ).order_by(desc(Incident.reported_at)).all()
    
    def get_critical_open(self) -> List[Incident]:
        """Получить критичные открытые инциденты"""
        return self.session.query(Incident).filter(
            and_(
                Incident.status.in_(['new', 'assigned', 'investigating']),
                Incident.severity.in_(['critical', 'high'])
            )
        ).order_by(desc(Incident.reported_at)).all()
    
    def get_assigned_to(self, assigned_to: str) -> List[Incident]:
        """Получить инциденты, назначенные пользователю"""
        return self.session.query(Incident).filter(
            Incident.assigned_to == assigned_to
        ).order_by(desc(Incident.reported_at)).all()
    
    def get_sla_breached(self) -> List[Incident]:
        """Получить инциденты с нарушением SLA"""
        return self.session.query(Incident).filter(
            Incident.sla_breached == True
        ).all()
    
    def generate_incident_number(self) -> str:
        """Генерирует новый номер инцидента"""
        today = datetime.now()
        year = today.year
        
        # Считаем инциденты за текущий год
        count = self.session.query(Incident).filter(
            Incident.incident_number.like(f'INC-{year}-%')
        ).count()
        
        return f"INC-{year}-{count + 1:04d}"


class ResponseActionRepository(BaseRepository):
    """Repository для Response Actions"""
    
    def __init__(self, session: Session):
        super().__init__(session, ResponseAction)
    
    def get_by_incident(self, incident_id: int) -> List[ResponseAction]:
        """Получить действия по инциденту"""
        return self.session.query(ResponseAction).filter(
            ResponseAction.incident_id == incident_id
        ).order_by(asc(ResponseAction.created_at)).all()
    
    def get_pending(self) -> List[ResponseAction]:
        """Получить ожидающие действия"""
        return self.session.query(ResponseAction).filter(
            ResponseAction.status == 'pending'
        ).all()
    
    def get_automated(self) -> List[ResponseAction]:
        """Получить автоматические действия"""
        return self.session.query(ResponseAction).filter(
            ResponseAction.automated == True
        ).all()
    
    def get_failed(self) -> List[ResponseAction]:
        """Получить неудавшиеся действия"""
        return self.session.query(ResponseAction).filter(
            ResponseAction.status == 'failed'
        ).all()
    
    def mark_as_completed(self, action_id: int, result: str = None) -> bool:
        """Отметить действие как завершенное"""
        action = self.get_by_id(action_id)
        if action:
            action.status = 'completed'
            action.completed_at = datetime.now()
            action.success = True
            if result:
                action.result = result
            self.session.flush()
            return True
        return False
    
    def mark_as_failed(self, action_id: int, error_message: str) -> bool:
        """Отметить действие как неудавшееся"""
        action = self.get_by_id(action_id)
        if action:
            action.status = 'failed'
            action.completed_at = datetime.now()
            action.success = False
            action.error_message = error_message
            self.session.flush()
            return True
        return False


class RepositoryFactory:
    """Factory для создания repositories"""
    
    def __init__(self, session: Session):
        self.session = session
    
    @property
    def assets(self) -> AssetRepository:
        return AssetRepository(self.session)
    
    @property
    def events(self) -> SecurityEventRepository:
        return SecurityEventRepository(self.session)
    
    @property
    def ioc(self) -> IoC_Repository:
        return IoC_Repository(self.session)
    
    @property
    def vulnerabilities(self) -> VulnerabilityRepository:
        return VulnerabilityRepository(self.session)
    
    @property
    def threats(self) -> ThreatRepository:
        return ThreatRepository(self.session)
    
    @property
    def incidents(self) -> IncidentRepository:
        return IncidentRepository(self.session)
    
    @property
    def response_actions(self) -> ResponseActionRepository:
        return ResponseActionRepository(self.session)
