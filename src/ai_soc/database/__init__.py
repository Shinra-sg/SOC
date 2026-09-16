"""
AI-SOC Database Package
"""

from .connection import (
    db,
    Base,
    DatabaseConnection,
    get_db_session,
    session_scope
)

from .models import (
    Asset,
    SecurityEvent,
    IndicatorOfCompromise,
    Vulnerability,
    Threat,
    Incident,
    ResponseAction
)

from .repositories import (
    AssetRepository,
    SecurityEventRepository,
    IoC_Repository,
    VulnerabilityRepository,
    ThreatRepository,
    IncidentRepository,
    ResponseActionRepository,
    RepositoryFactory
)

__all__ = [
    # Connection
    'db',
    'Base',
    'DatabaseConnection',
    'get_db_session',
    'session_scope',
    
    # Models
    'Asset',
    'SecurityEvent',
    'IndicatorOfCompromise',
    'Vulnerability',
    'Threat',
    'Incident',
    'ResponseAction',
    
    # Repositories
    'AssetRepository',
    'SecurityEventRepository',
    'IoC_Repository',
    'VulnerabilityRepository',
    'ThreatRepository',
    'IncidentRepository',
    'ResponseActionRepository',
    'RepositoryFactory',
]
