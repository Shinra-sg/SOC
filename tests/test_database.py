"""
Tests для Database Layer
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from ai_soc.database import (
    Base, db, session_scope,
    Asset, SecurityEvent, IndicatorOfCompromise, Vulnerability,
    AssetRepository, SecurityEventRepository, IoC_Repository,
    VulnerabilityRepository, RepositoryFactory
)


@pytest.fixture
def test_db():
    """Создает временную тестовую БД"""
    # Use in-memory SQLite for tests
    engine = create_engine('sqlite:///:memory:', echo=False)
    Base.metadata.create_all(engine)
    
    from sqlalchemy.orm import sessionmaker
    Session = sessionmaker(bind=engine)
    session = Session()
    
    yield session
    
    session.close()


def test_asset_repository_create(test_db):
    """Тест создания asset"""
    repo = AssetRepository(test_db)
    
    asset = repo.create(
        asset_name='test-server-01',
        asset_type='server',
        ip_address='192.168.1.100',
        criticality='high',
        status='active'
    )
    
    test_db.commit()
    
    assert asset.id is not None
    assert asset.asset_name == 'test-server-01'
    assert asset.asset_type == 'server'
    assert asset.criticality == 'high'


def test_asset_repository_get_by_ip(test_db):
    """Тест получения asset по IP"""
    repo = AssetRepository(test_db)
    
    # Create
    repo.create(
        asset_name='web-server',
        asset_type='server',
        ip_address='10.0.0.1',
        criticality='critical'
    )
    test_db.commit()
    
    # Get by IP
    asset = repo.get_by_ip('10.0.0.1')
    
    assert asset is not None
    assert asset.asset_name == 'web-server'
    assert asset.ip_address == '10.0.0.1'


def test_asset_repository_get_critical(test_db):
    """Тест получения критичных assets"""
    repo = AssetRepository(test_db)
    
    # Create assets
    repo.create(asset_name='critical-1', asset_type='server', criticality='critical')
    repo.create(asset_name='high-1', asset_type='server', criticality='high')
    repo.create(asset_name='medium-1', asset_type='server', criticality='medium')
    test_db.commit()
    
    # Get critical
    critical_assets = repo.get_critical_assets()
    
    assert len(critical_assets) == 2  # critical + high
    assert all(a.criticality in ['critical', 'high'] for a in critical_assets)


def test_security_event_repository_create(test_db):
    """Тест создания security event"""
    repo = SecurityEventRepository(test_db)
    
    event = repo.create(
        event_timestamp=datetime.now().isoformat(),
        source_system='firewall',
        source_ip='45.142.212.100',
        destination_ip='192.168.1.10',
        event_type='port_scan',
        event_category='network',
        severity='high',
        event_description='Port scan detected'
    )
    
    test_db.commit()
    
    assert event.id is not None
    assert event.event_type == 'port_scan'
    assert event.severity == 'high'


def test_security_event_repository_get_unprocessed(test_db):
    """Тест получения необработанных событий"""
    repo = SecurityEventRepository(test_db)
    
    # Create events
    repo.create(
        event_timestamp=datetime.now().isoformat(),
        source_system='ids',
        event_type='test1',
        event_category='network',
        processed=False
    )
    repo.create(
        event_timestamp=datetime.now().isoformat(),
        source_system='ids',
        event_type='test2',
        event_category='network',
        processed=True
    )
    test_db.commit()
    
    # Get unprocessed
    unprocessed = repo.get_unprocessed()
    
    assert len(unprocessed) == 1
    assert unprocessed[0].event_type == 'test1'


def test_ioc_repository_check_ip(test_db):
    """Тест проверки IP в IoC"""
    repo = IoC_Repository(test_db)
    
    # Create malicious IP
    repo.create(
        ioc_type='ip_address',
        ioc_value='45.142.212.100',
        threat_type='malware',
        severity='high',
        source='VirusTotal',
        is_active=True
    )
    test_db.commit()
    
    # Check IP
    ioc = repo.check_ip('45.142.212.100')
    
    assert ioc is not None
    assert ioc.ioc_value == '45.142.212.100'
    assert ioc.threat_type == 'malware'
    
    # Check non-existent IP
    ioc_none = repo.check_ip('1.1.1.1')
    assert ioc_none is None


def test_vulnerability_repository_get_by_asset(test_db):
    """Тест получения уязвимостей по asset"""
    asset_repo = AssetRepository(test_db)
    vuln_repo = VulnerabilityRepository(test_db)
    
    # Create asset
    asset = asset_repo.create(
        asset_name='vuln-server',
        asset_type='server'
    )
    test_db.commit()
    
    # Create vulnerabilities
    vuln_repo.create(
        asset_id=asset.id,
        cve_id='CVE-2021-44228',
        vulnerability_name='Log4Shell',
        severity='critical',
        cvss_score=10.0
    )
    vuln_repo.create(
        asset_id=asset.id,
        cve_id='CVE-2022-0001',
        vulnerability_name='Test Vuln',
        severity='high',
        cvss_score=8.5
    )
    test_db.commit()
    
    # Get by asset
    vulns = vuln_repo.get_by_asset(asset.id)
    
    assert len(vulns) == 2
    assert all(v.asset_id == asset.id for v in vulns)


def test_repository_factory(test_db):
    """Тест RepositoryFactory"""
    factory = RepositoryFactory(test_db)
    
    # Test all repositories accessible
    assert isinstance(factory.assets, AssetRepository)
    assert isinstance(factory.events, SecurityEventRepository)
    assert isinstance(factory.ioc, IoC_Repository)
    assert isinstance(factory.vulnerabilities, VulnerabilityRepository)


def test_session_scope():
    """Тест session scope context manager"""
    # Set test environment
    os.environ['DB_TYPE'] = 'sqlite'
    os.environ['DB_PATH'] = ':memory:'
    
    # Test context manager
    with session_scope() as session:
        # Create asset
        asset = Asset(
            asset_name='scope-test',
            asset_type='server'
        )
        session.add(asset)
    
    # Session should be committed automatically
    with session_scope() as session:
        found = session.query(Asset).filter(Asset.asset_name == 'scope-test').first()
        assert found is not None


def test_crud_operations(test_db):
    """Тест базовых CRUD операций"""
    repo = AssetRepository(test_db)
    
    # CREATE
    asset = repo.create(
        asset_name='crud-test',
        asset_type='workstation',
        status='active'
    )
    test_db.commit()
    asset_id = asset.id
    
    # READ
    found = repo.get_by_id(asset_id)
    assert found is not None
    assert found.asset_name == 'crud-test'
    
    # UPDATE
    updated = repo.update(asset_id, status='inactive')
    test_db.commit()
    assert updated.status == 'inactive'
    
    # DELETE
    deleted = repo.delete(asset_id)
    test_db.commit()
    assert deleted is True
    
    # Verify deleted
    not_found = repo.get_by_id(asset_id)
    assert not_found is None


def test_count_operations(test_db):
    """Тест подсчета записей"""
    repo = AssetRepository(test_db)
    
    # Initial count
    initial = repo.count()
    
    # Add assets
    repo.create(asset_name='count-1', asset_type='server')
    repo.create(asset_name='count-2', asset_type='server')
    repo.create(asset_name='count-3', asset_type='server')
    test_db.commit()
    
    # Check count
    final = repo.count()
    assert final == initial + 3


if __name__ == "__main__":
    print("Running database tests...")
    pytest.main([__file__, '-v'])
