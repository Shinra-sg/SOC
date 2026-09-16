#!/usr/bin/env python3
"""
Simple Database Layer Test
Тест без pytest - просто запуск
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

os.environ['DB_TYPE'] = 'sqlite'
os.environ['DB_PATH'] = 'database/test_db_layer.db'

from ai_soc.database import (
    db, session_scope,
    Asset, SecurityEvent, IndicatorOfCompromise,
    AssetRepository, SecurityEventRepository, IoC_Repository,
    RepositoryFactory
)
from datetime import datetime


def test_connection():
    """Тест подключения к БД"""
    print("\n1. Testing database connection...")
    try:
        # Create tables
        db.create_all_tables()
        print("   ✓ Tables created successfully")
        return True
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        return False


def test_asset_crud():
    """Тест CRUD операций для Asset"""
    print("\n2. Testing Asset CRUD operations...")
    
    try:
        with session_scope() as session:
            repo = AssetRepository(session)
            
            # CREATE
            asset = repo.create(
                asset_name='test-server-01',
                asset_type='server',
                ip_address='192.168.1.100',
                criticality='high',
                status='active'
            )
            print(f"   ✓ Created: {asset}")
            
            asset_id = asset.id
        
        # READ
        with session_scope() as session:
            repo = AssetRepository(session)
            found = repo.get_by_id(asset_id)
            assert found is not None
            assert found.asset_name == 'test-server-01'
            print(f"   ✓ Read: {found}")
            
            # Get by IP
            by_ip = repo.get_by_ip('192.168.1.100')
            assert by_ip is not None
            print(f"   ✓ Get by IP: {by_ip.asset_name}")
        
        # UPDATE
        with session_scope() as session:
            repo = AssetRepository(session)
            updated = repo.update(asset_id, status='inactive')
            assert updated.status == 'inactive'
            print(f"   ✓ Updated status to: {updated.status}")
        
        # DELETE
        with session_scope() as session:
            repo = AssetRepository(session)
            deleted = repo.delete(asset_id)
            assert deleted is True
            print("   ✓ Deleted successfully")
        
        print("   ✓ All Asset CRUD operations passed")
        return True
        
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_security_events():
    """Тест Security Events"""
    print("\n3. Testing Security Events...")
    
    try:
        with session_scope() as session:
            repo = SecurityEventRepository(session)
            
            # Create events
            event1 = repo.create(
                event_timestamp=datetime.now().isoformat(),
                source_system='firewall',
                source_ip='45.142.212.100',
                destination_ip='192.168.1.10',
                event_type='port_scan',
                event_category='network',
                severity='high',
                event_description='Port scan detected',
                processed=False
            )
            
            event2 = repo.create(
                event_timestamp=datetime.now().isoformat(),
                source_system='ids',
                source_ip='45.142.212.100',
                destination_ip='192.168.1.20',
                event_type='failed_login',
                event_category='authentication',
                severity='medium',
                event_description='Failed login attempt',
                processed=True
            )
            
            print(f"   ✓ Created 2 events")
            
            # Get unprocessed
            unprocessed = repo.get_unprocessed()
            assert len(unprocessed) >= 1
            print(f"   ✓ Found {len(unprocessed)} unprocessed events")
            
            # Get by source IP
            by_ip = repo.get_by_source_ip('45.142.212.100')
            assert len(by_ip) >= 2
            print(f"   ✓ Found {len(by_ip)} events from IP")
            
            # Get critical
            critical = repo.get_critical_events()
            print(f"   ✓ Found {len(critical)} critical/high events")
            
            # Mark as processed
            marked = repo.mark_as_processed(event1.id)
            assert marked is True
            print("   ✓ Marked event as processed")
        
        print("   ✓ All Security Event operations passed")
        return True
        
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_ioc():
    """Тест Indicators of Compromise"""
    print("\n4. Testing Indicators of Compromise...")
    
    try:
        with session_scope() as session:
            repo = IoC_Repository(session)
            
            # Create IoCs
            ioc_ip = repo.create(
                ioc_type='ip_address',
                ioc_value='45.142.212.100',
                threat_type='malware',
                severity='high',
                confidence_score=95,
                source='VirusTotal',
                is_active=True
            )
            
            ioc_domain = repo.create(
                ioc_type='domain',
                ioc_value='malicious-site.xyz',
                threat_type='phishing',
                severity='high',
                confidence_score=90,
                source='URLhaus',
                is_active=True
            )
            
            print("   ✓ Created 2 IoCs")
            
            # Check IP
            found_ip = repo.check_ip('45.142.212.100')
            assert found_ip is not None
            assert found_ip.threat_type == 'malware'
            print(f"   ✓ IP check: {found_ip.ioc_value} is {found_ip.threat_type}")
            
            # Check domain
            found_domain = repo.check_domain('malicious-site.xyz')
            assert found_domain is not None
            print(f"   ✓ Domain check: {found_domain.ioc_value} is {found_domain.threat_type}")
            
            # Check non-existent
            not_found = repo.check_ip('1.1.1.1')
            assert not_found is None
            print("   ✓ Non-existent IP returns None")
            
            # Get active
            active = repo.get_active()
            assert len(active) >= 2
            print(f"   ✓ Found {len(active)} active IoCs")
        
        print("   ✓ All IoC operations passed")
        return True
        
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_repository_factory():
    """Тест RepositoryFactory"""
    print("\n5. Testing RepositoryFactory...")
    
    try:
        with session_scope() as session:
            factory = RepositoryFactory(session)
            
            # Test all repositories accessible
            assert factory.assets is not None
            assert factory.events is not None
            assert factory.ioc is not None
            assert factory.vulnerabilities is not None
            assert factory.threats is not None
            assert factory.incidents is not None
            assert factory.response_actions is not None
            
            print("   ✓ All repositories accessible via factory")
            
            # Test using factory
            asset = factory.assets.create(
                asset_name='factory-test',
                asset_type='server'
            )
            print(f"   ✓ Created asset via factory: {asset.asset_name}")
            
            count = factory.assets.count()
            print(f"   ✓ Asset count: {count}")
        
        print("   ✓ RepositoryFactory test passed")
        return True
        
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_statistics():
    """Тест статистики"""
    print("\n6. Testing statistics...")
    
    try:
        with session_scope() as session:
            repo = SecurityEventRepository(session)
            stats = repo.get_statistics()
            
            print(f"   ✓ Total events: {stats['total']}")
            print(f"   ✓ Critical: {stats['critical']}")
            print(f"   ✓ High: {stats['high']}")
            print(f"   ✓ By category: {stats['by_category']}")
        
        print("   ✓ Statistics test passed")
        return True
        
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        return False


def cleanup():
    """Очистка тестовой БД"""
    print("\n7. Cleanup...")
    try:
        test_db_path = Path('database/test_db_layer.db')
        if test_db_path.exists():
            test_db_path.unlink()
            print("   ✓ Test database removed")
    except Exception as e:
        print(f"   ⚠ Cleanup warning: {e}")


def main():
    """Main entry point"""
    print("\n" + "="*70)
    print("AI-SOC Database Layer Test")
    print("="*70)
    
    tests = [
        test_connection,
        test_asset_crud,
        test_security_events,
        test_ioc,
        test_repository_factory,
        test_statistics
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"\n✗ Test {test.__name__} failed with exception: {e}")
            failed += 1
    
    print("\n" + "="*70)
    print(f"Results: {passed} passed, {failed} failed")
    print("="*70)
    
    if failed == 0:
        print("\n✅ ALL TESTS PASSED!")
    else:
        print(f"\n❌ {failed} TESTS FAILED!")
    
    # Cleanup
    cleanup()
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
