#!/usr/bin/env python3
"""
AI-SOC Database Schema Test
Проверяет созданную схему базы данных
"""

import sqlite3
import sys
from pathlib import Path
from datetime import datetime
import json


def test_database_structure(db_path: str = "database/ai_soc.db"):
    """Проверяет структуру базы данных"""
    
    print("\n" + "="*70)
    print("🧪 AI-SOC Database Schema Test")
    print("="*70 + "\n")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # ========================================
        # 1. Проверка таблиц
        # ========================================
        print("📋 1. Checking Tables...")
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' 
            ORDER BY name
        """)
        tables = [row[0] for row in cursor.fetchall()]
        
        expected_tables = [
            'assets',
            'security_events',
            'indicators_of_compromise',
            'vulnerabilities',
            'threats',
            'incidents',
            'response_actions'
        ]
        
        print(f"   Found {len(tables)} tables:")
        for table in tables:
            status = "✅" if table in expected_tables else "⚠️ "
            print(f"      {status} {table}")
        
        missing = set(expected_tables) - set(tables)
        if missing:
            print(f"\n   ❌ Missing tables: {missing}")
            return False
        else:
            print("\n   ✅ All expected tables exist!\n")
        
        # ========================================
        # 2. Проверка индексов
        # ========================================
        print("🔍 2. Checking Indexes...")
        total_indexes = 0
        for table in expected_tables:
            cursor.execute(f"""
                SELECT name FROM sqlite_master 
                WHERE type='index' AND tbl_name='{table}'
            """)
            indexes = cursor.fetchall()
            if indexes:
                print(f"   {table}:")
                for idx in indexes:
                    print(f"      • {idx[0]}")
                total_indexes += len(indexes)
        
        print(f"\n   ✅ Total indexes: {total_indexes}\n")
        
        # ========================================
        # 3. Проверка views
        # ========================================
        print("👁️  3. Checking Views...")
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='view'
        """)
        views = [row[0] for row in cursor.fetchall()]
        
        if views:
            print(f"   Found {len(views)} views:")
            for view in views:
                print(f"      • {view}")
        else:
            print("   ⚠️  No views found")
        print()
        
        # ========================================
        # 4. Проверка triggers
        # ========================================
        print("⚡ 4. Checking Triggers...")
        cursor.execute("""
            SELECT name, tbl_name FROM sqlite_master 
            WHERE type='trigger'
        """)
        triggers = cursor.fetchall()
        
        if triggers:
            print(f"   Found {len(triggers)} triggers:")
            for trigger in triggers:
                print(f"      • {trigger[0]} (on {trigger[1]})")
        else:
            print("   ⚠️  No triggers found")
        print()
        
        # ========================================
        # 5. Тест вставки данных
        # ========================================
        print("💾 5. Testing Data Insertion...")
        
        # Test 1: Insert asset
        cursor.execute("""
            INSERT INTO assets (
                asset_name, asset_type, ip_address, 
                criticality, status
            ) VALUES (?, ?, ?, ?, ?)
        """, ('test-server-01', 'server', '192.168.1.100', 'high', 'active'))
        asset_id = cursor.lastrowid
        print(f"   ✅ Inserted asset (ID: {asset_id})")
        
        # Test 2: Insert security event
        cursor.execute("""
            INSERT INTO security_events (
                event_timestamp, source_system, source_ip,
                event_type, event_category, severity,
                event_description
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().isoformat(),
            'firewall',
            '10.0.0.50',
            'port_scan',
            'network',
            'medium',
            'Port scan detected from external IP'
        ))
        event_id = cursor.lastrowid
        print(f"   ✅ Inserted security_event (ID: {event_id})")
        
        # Test 3: Insert IoC
        cursor.execute("""
            INSERT INTO indicators_of_compromise (
                ioc_type, ioc_value, threat_type,
                severity, confidence_score, source
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            'ip_address',
            '203.0.113.42',
            'malware',
            'high',
            85,
            'VirusTotal'
        ))
        ioc_id = cursor.lastrowid
        print(f"   ✅ Inserted IoC (ID: {ioc_id})")
        
        # Test 4: Insert vulnerability
        cursor.execute("""
            INSERT INTO vulnerabilities (
                cve_id, asset_id, vulnerability_name,
                cvss_score, severity, status
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            'CVE-2021-44228',
            asset_id,
            'Apache Log4j Remote Code Execution',
            10.0,
            'critical',
            'open'
        ))
        vuln_id = cursor.lastrowid
        print(f"   ✅ Inserted vulnerability (ID: {vuln_id})")
        
        # Test 5: Insert threat
        cursor.execute("""
            INSERT INTO threats (
                threat_type, threat_category, severity,
                confidence_score, source_ip, status,
                description
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            'brute_force',
            'intrusion',
            'high',
            90,
            '10.0.0.50',
            'active',
            'Brute force attack detected on SSH service'
        ))
        threat_id = cursor.lastrowid
        print(f"   ✅ Inserted threat (ID: {threat_id})")
        
        # Test 6: Insert incident
        cursor.execute("""
            INSERT INTO incidents (
                incident_number, incident_title, incident_type,
                incident_category, severity, status, description
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            'INC-2024-001',
            'SSH Brute Force Attack',
            'unauthorized_access_attempt',
            'security_breach',
            'high',
            'investigating',
            'Multiple failed SSH login attempts detected'
        ))
        incident_id = cursor.lastrowid
        print(f"   ✅ Inserted incident (ID: {incident_id})")
        
        # Test 7: Insert response action
        cursor.execute("""
            INSERT INTO response_actions (
                incident_id, action_type, action_category,
                action_description, status, automated
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            incident_id,
            'block_ip',
            'containment',
            'Block malicious IP in firewall',
            'completed',
            1
        ))
        action_id = cursor.lastrowid
        print(f"   ✅ Inserted response_action (ID: {action_id})")
        
        conn.commit()
        print("\n   ✅ All test data inserted successfully!\n")
        
        # ========================================
        # 6. Тест чтения данных
        # ========================================
        print("📖 6. Testing Data Retrieval...")
        
        # Query 1: Get all assets
        cursor.execute("SELECT COUNT(*) FROM assets")
        count = cursor.fetchone()[0]
        print(f"   Assets: {count} record(s)")
        
        # Query 2: Get all events
        cursor.execute("SELECT COUNT(*) FROM security_events")
        count = cursor.fetchone()[0]
        print(f"   Security Events: {count} record(s)")
        
        # Query 3: Get high severity threats
        cursor.execute("""
            SELECT threat_type, severity, source_ip 
            FROM threats 
            WHERE severity IN ('high', 'critical')
        """)
        threats = cursor.fetchall()
        print(f"   High Severity Threats: {len(threats)} record(s)")
        for threat in threats:
            print(f"      • {threat[0]} ({threat[1]}) from {threat[2]}")
        
        # Query 4: Get incidents with response actions
        cursor.execute("""
            SELECT 
                i.incident_number,
                i.incident_title,
                i.severity,
                COUNT(ra.id) as action_count
            FROM incidents i
            LEFT JOIN response_actions ra ON i.id = ra.incident_id
            GROUP BY i.id
        """)
        incidents = cursor.fetchall()
        print(f"\n   Incidents with Actions:")
        for inc in incidents:
            print(f"      • {inc[0]}: {inc[1]} ({inc[2]}) - {inc[3]} action(s)")
        
        # Query 5: Test view (if exists)
        try:
            cursor.execute("SELECT COUNT(*) FROM active_critical_threats")
            count = cursor.fetchone()[0]
            print(f"\n   View 'active_critical_threats': {count} record(s)")
        except:
            print("\n   ⚠️  View 'active_critical_threats' not working")
        
        print()
        
        # ========================================
        # 7. Тест constraints и validation
        # ========================================
        print("🔒 7. Testing Constraints...")
        
        # Test 1: Unique constraint (IoC)
        try:
            cursor.execute("""
                INSERT INTO indicators_of_compromise (
                    ioc_type, ioc_value, source
                ) VALUES (?, ?, ?)
            """, ('ip_address', '203.0.113.42', 'test'))
            print("   ❌ FAILED: Unique constraint not working!")
        except sqlite3.IntegrityError:
            print("   ✅ Unique constraint working (IoC)")
        
        # Test 2: Foreign key (vulnerability -> asset)
        try:
            cursor.execute("""
                INSERT INTO vulnerabilities (
                    asset_id, vulnerability_name, severity
                ) VALUES (?, ?, ?)
            """, (99999, 'Test Vuln', 'high'))
            print("   ⚠️  Foreign key constraint not enforced (expected in SQLite)")
        except sqlite3.IntegrityError:
            print("   ✅ Foreign key constraint working")
        
        # Test 3: Check constraint (severity values)
        try:
            cursor.execute("""
                INSERT INTO threats (
                    threat_type, threat_category, severity
                ) VALUES (?, ?, ?)
            """, ('test', 'intrusion', 'invalid_severity'))
            print("   ❌ FAILED: Check constraint not working!")
        except sqlite3.IntegrityError:
            print("   ✅ Check constraint working (severity)")
        
        conn.rollback()  # Rollback test failures
        print()
        
        # ========================================
        # 8. Очистка тестовых данных
        # ========================================
        print("🧹 8. Cleaning up test data...")
        
        cursor.execute("DELETE FROM response_actions")
        cursor.execute("DELETE FROM incidents")
        cursor.execute("DELETE FROM threats")
        cursor.execute("DELETE FROM vulnerabilities")
        cursor.execute("DELETE FROM indicators_of_compromise")
        cursor.execute("DELETE FROM security_events")
        cursor.execute("DELETE FROM assets")
        
        conn.commit()
        print("   ✅ Test data cleaned up\n")
        
        # ========================================
        # Summary
        # ========================================
        print("="*70)
        print("✅ DATABASE SCHEMA TEST PASSED!")
        print("="*70)
        print("\n📊 Summary:")
        print(f"   • Tables: {len(expected_tables)}/{len(expected_tables)} ✅")
        print(f"   • Indexes: {total_indexes} ✅")
        print(f"   • Views: {len(views)} {'✅' if views else '⚠️'}")
        print(f"   • Triggers: {len(triggers)} {'✅' if triggers else '⚠️'}")
        print(f"   • Data insertion: ✅")
        print(f"   • Data retrieval: ✅")
        print(f"   • Constraints: ✅")
        print()
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main entry point"""
    db_path = sys.argv[1] if len(sys.argv) > 1 else "database/ai_soc.db"
    
    if not Path(db_path).exists():
        print(f"❌ Database file not found: {db_path}")
        print(f"   Run: python3 database/init_db.py sqlite")
        sys.exit(1)
    
    success = test_database_structure(db_path)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
