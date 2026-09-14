#!/usr/bin/env python3
"""
AI-SOC Realistic Data Test
Тест с реалистичными данными SOC сценариев
"""

import sqlite3
import sys
from pathlib import Path
from datetime import datetime, timedelta
import random
import json


def test_realistic_scenarios(db_path: str = "database/ai_soc.db"):
    """Тестирует БД с реалистичными SOC сценариями"""
    
    print("\n" + "="*70)
    print("🎭 AI-SOC Realistic Scenarios Test")
    print("="*70 + "\n")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # ========================================
        # Сценарий 1: Brute Force атака
        # ========================================
        print("🔴 Scenario 1: SSH Brute Force Attack")
        print("-" * 70)
        
        # Создаем атакующий IP в IoC
        cursor.execute("""
            INSERT INTO indicators_of_compromise (
                ioc_type, ioc_value, threat_type, severity,
                confidence_score, source, description
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            'ip_address',
            '45.142.212.100',
            'brute_force',
            'high',
            95,
            'AbuseIPDB',
            'Known brute force attacker'
        ))
        ioc_id = cursor.lastrowid
        print(f"   ✓ Created IoC for malicious IP (ID: {ioc_id})")
        
        # Создаем целевой сервер
        cursor.execute("""
            INSERT INTO assets (
                asset_name, asset_type, ip_address,
                hostname, criticality, status, os_name
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            'web-server-01',
            'server',
            '192.168.1.10',
            'web01.company.local',
            'critical',
            'active',
            'Ubuntu 22.04'
        ))
        asset_id = cursor.lastrowid
        print(f"   ✓ Created target server (ID: {asset_id})")
        
        # Генерируем серию failed login events
        event_ids = []
        base_time = datetime.now()
        for i in range(15):
            cursor.execute("""
                INSERT INTO security_events (
                    event_timestamp, source_system, source_ip, destination_ip,
                    event_type, event_category, severity,
                    event_description, username, protocol
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                (base_time - timedelta(minutes=i)).isoformat(),
                'auth',
                '45.142.212.100',
                '192.168.1.10',
                'failed_login',
                'authentication',
                'medium',
                f'Failed SSH login attempt #{16-i}',
                random.choice(['root', 'admin', 'user', 'test']),
                'SSH'
            ))
            event_ids.append(cursor.lastrowid)
        
        print(f"   ✓ Generated {len(event_ids)} failed login events")
        
        # Создаем threat
        cursor.execute("""
            INSERT INTO threats (
                source_event_ids, primary_event_id, threat_type,
                threat_category, severity, confidence_score,
                source_ip, target_ip, detection_method,
                mitre_tactic, mitre_technique, description, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            json.dumps(event_ids),
            event_ids[0],
            'brute_force',
            'intrusion',
            'high',
            95,
            '45.142.212.100',
            '192.168.1.10',
            'signature',
            'Initial Access',
            'T1078',
            'SSH brute force attack detected: 15 failed login attempts in 15 minutes',
            'active'
        ))
        threat_id = cursor.lastrowid
        print(f"   ✓ Created threat (ID: {threat_id})")
        
        # Создаем incident
        cursor.execute("""
            INSERT INTO incidents (
                incident_number, incident_title, threat_ids,
                primary_threat_id, incident_type, incident_category,
                severity, status, description, assigned_to
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            'INC-2024-001',
            'SSH Brute Force Attack on web-server-01',
            json.dumps([threat_id]),
            threat_id,
            'unauthorized_access_attempt',
            'security_breach',
            'high',
            'investigating',
            'Multiple failed SSH login attempts from known malicious IP',
            'SOC Analyst'
        ))
        incident_id = cursor.lastrowid
        print(f"   ✓ Created incident {incident_id} (INC-2024-001)")
        
        # Автоматическая блокировка IP
        cursor.execute("""
            INSERT INTO response_actions (
                incident_id, threat_id, action_type, action_category,
                action_description, target_ip, status,
                automated, executed_by, result, success
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            incident_id,
            threat_id,
            'block_ip',
            'containment',
            'Block malicious IP 45.142.212.100 in firewall',
            '45.142.212.100',
            'completed',
            1,
            'system',
            'IP blocked successfully',
            1
        ))
        print(f"   ✓ Automated response: IP blocked\n")
        
        # ========================================
        # Сценарий 2: Malware Detection
        # ========================================
        print("🔴 Scenario 2: Malware Detection")
        print("-" * 70)
        
        # Malicious file hash в IoC
        cursor.execute("""
            INSERT INTO indicators_of_compromise (
                ioc_type, ioc_value, hash_type, threat_type,
                malware_family, severity, confidence_score, source
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            'file_hash',
            'd41d8cd98f00b204e9800998ecf8427e',
            'MD5',
            'malware',
            'Emotet',
            'critical',
            98,
            'VirusTotal'
        ))
        malware_ioc_id = cursor.lastrowid
        print(f"   ✓ Created malware IoC (ID: {malware_ioc_id})")
        
        # Workstation с малварью
        cursor.execute("""
            INSERT INTO assets (
                asset_name, asset_type, ip_address,
                criticality, status, os_name, owner
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            'ws-finance-05',
            'workstation',
            '192.168.10.45',
            'high',
            'compromised',
            'Windows 10',
            'John Doe'
        ))
        infected_asset_id = cursor.lastrowid
        print(f"   ✓ Created infected workstation (ID: {infected_asset_id})")
        
        # Malware detection event
        cursor.execute("""
            INSERT INTO security_events (
                event_timestamp, source_system, source_asset_id,
                event_type, event_category, severity,
                event_description, parsed_data
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().isoformat(),
            'endpoint_protection',
            infected_asset_id,
            'malware_detected',
            'malware',
            'critical',
            'Emotet malware detected and quarantined',
            json.dumps({
                'file_path': 'C:\\Users\\jdoe\\Downloads\\invoice.doc',
                'hash_md5': 'd41d8cd98f00b204e9800998ecf8427e',
                'action_taken': 'quarantined'
            })
        ))
        malware_event_id = cursor.lastrowid
        print(f"   ✓ Malware detection event created (ID: {malware_event_id})")
        
        # Threat
        cursor.execute("""
            INSERT INTO threats (
                primary_event_id, threat_type, threat_category,
                severity, confidence_score, detection_method,
                mitre_tactic, mitre_technique, description, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            malware_event_id,
            'malware',
            'malware',
            'critical',
            98,
            'signature',
            'Execution',
            'T1204',
            'Emotet banking trojan detected on finance workstation',
            'contained'
        ))
        malware_threat_id = cursor.lastrowid
        print(f"   ✓ Malware threat created (ID: {malware_threat_id})")
        
        # Incident
        cursor.execute("""
            INSERT INTO incidents (
                incident_number, incident_title,
                incident_type, incident_category,
                severity, status, description
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            'INC-2024-002',
            'Emotet Malware on Finance Workstation',
            'malware_infection',
            'malware_infection',
            'critical',
            'recovering',
            'Emotet banking trojan detected and contained'
        ))
        malware_incident_id = cursor.lastrowid
        print(f"   ✓ Malware incident created (ID: {malware_incident_id})")
        
        # Response actions
        actions = [
            ('isolate_host', 'containment', 'Isolate infected workstation from network'),
            ('quarantine_file', 'eradication', 'Quarantine malicious file'),
            ('reset_password', 'eradication', 'Force password reset for user'),
            ('collect_evidence', 'investigation', 'Collect forensic evidence')
        ]
        
        for action_type, category, description in actions:
            cursor.execute("""
                INSERT INTO response_actions (
                    incident_id, action_type, action_category,
                    action_description, status, automated
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                malware_incident_id,
                action_type,
                category,
                description,
                'completed',
                0
            ))
        
        print(f"   ✓ {len(actions)} response actions executed\n")
        
        # ========================================
        # Сценарий 3: Vulnerability Scan
        # ========================================
        print("🔴 Scenario 3: Critical Vulnerability Discovered")
        print("-" * 70)
        
        # Web server (уже создан выше, используем asset_id)
        
        # Critical CVE
        cursor.execute("""
            INSERT INTO vulnerabilities (
                cve_id, asset_id, vulnerability_name,
                cvss_score, cvss_vector, severity,
                vulnerability_type, affected_software, affected_version,
                exploit_available, patch_available, patch_version,
                status, priority, assigned_to, scan_date, scanner_name
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            'CVE-2021-44228',
            asset_id,
            'Apache Log4j2 Remote Code Execution Vulnerability',
            10.0,
            'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H',
            'critical',
            'RCE',
            'Apache Log4j',
            '2.14.1',
            1,
            1,
            '2.17.0',
            'open',
            'critical',
            'DevOps Team',
            datetime.now().isoformat(),
            'Nessus'
        ))
        vuln_id = cursor.lastrowid
        print(f"   ✓ Critical vulnerability discovered (ID: {vuln_id})")
        print(f"      CVE-2021-44228 (Log4Shell)")
        print(f"      CVSS Score: 10.0 (CRITICAL)")
        print(f"      Affected: web-server-01\n")
        
        conn.commit()
        
        # ========================================
        # Query Results
        # ========================================
        print("="*70)
        print("📊 SOC Dashboard Summary")
        print("="*70 + "\n")
        
        # Active incidents
        cursor.execute("""
            SELECT incident_number, incident_title, severity, status
            FROM incidents
            WHERE status NOT IN ('resolved', 'closed')
            ORDER BY severity DESC
        """)
        incidents = cursor.fetchall()
        print(f"🚨 Active Incidents: {len(incidents)}")
        for inc in incidents:
            print(f"   • {inc[0]}: {inc[1]}")
            print(f"     Severity: {inc[2].upper()} | Status: {inc[3]}")
        
        print()
        
        # Critical threats
        cursor.execute("""
            SELECT threat_type, severity, source_ip, status
            FROM threats
            WHERE severity IN ('critical', 'high')
            ORDER BY detection_timestamp DESC
        """)
        threats = cursor.fetchall()
        print(f"⚠️  High/Critical Threats: {len(threats)}")
        for threat in threats:
            print(f"   • {threat[0].upper()} ({threat[1]})")
            print(f"     Source: {threat[2] or 'N/A'} | Status: {threat[3]}")
        
        print()
        
        # Vulnerable assets
        cursor.execute("""
            SELECT 
                a.asset_name,
                v.cve_id,
                v.cvss_score,
                v.severity
            FROM vulnerabilities v
            JOIN assets a ON v.asset_id = a.id
            WHERE v.status = 'open'
            ORDER BY v.cvss_score DESC
        """)
        vulns = cursor.fetchall()
        print(f"🔓 Open Vulnerabilities: {len(vulns)}")
        for vuln in vulns:
            print(f"   • {vuln[0]}: {vuln[1]} (CVSS: {vuln[2]})")
        
        print()
        
        # Response actions stats
        cursor.execute("""
            SELECT 
                action_type,
                COUNT(*) as count,
                SUM(CASE WHEN automated = 1 THEN 1 ELSE 0 END) as automated_count
            FROM response_actions
            GROUP BY action_type
            ORDER BY count DESC
        """)
        actions_stats = cursor.fetchall()
        print(f"🛡️  Response Actions Summary:")
        for action in actions_stats:
            print(f"   • {action[0]}: {action[1]} total ({action[2]} automated)")
        
        print()
        
        # IoC stats
        cursor.execute("""
            SELECT 
                ioc_type,
                COUNT(*) as count,
                SUM(CASE WHEN severity = 'critical' THEN 1 ELSE 0 END) as critical_count
            FROM indicators_of_compromise
            GROUP BY ioc_type
        """)
        ioc_stats = cursor.fetchall()
        print(f"🎯 Indicators of Compromise:")
        for ioc in ioc_stats:
            print(f"   • {ioc[0]}: {ioc[1]} total ({ioc[2]} critical)")
        
        print()
        
        # Asset stats
        cursor.execute("""
            SELECT 
                asset_type,
                COUNT(*) as count,
                SUM(CASE WHEN status = 'compromised' THEN 1 ELSE 0 END) as compromised
            FROM assets
            GROUP BY asset_type
        """)
        asset_stats = cursor.fetchall()
        print(f"💻 Assets Overview:")
        for asset in asset_stats:
            print(f"   • {asset[0]}: {asset[1]} total ({asset[2]} compromised)")
        
        print("\n" + "="*70)
        print("✅ REALISTIC SCENARIOS TEST COMPLETED!")
        print("="*70)
        print("\n📈 Statistics:")
        cursor.execute("SELECT COUNT(*) FROM assets")
        print(f"   • Assets: {cursor.fetchone()[0]}")
        cursor.execute("SELECT COUNT(*) FROM security_events")
        print(f"   • Security Events: {cursor.fetchone()[0]}")
        cursor.execute("SELECT COUNT(*) FROM threats")
        print(f"   • Threats: {cursor.fetchone()[0]}")
        cursor.execute("SELECT COUNT(*) FROM incidents")
        print(f"   • Incidents: {cursor.fetchone()[0]}")
        cursor.execute("SELECT COUNT(*) FROM response_actions")
        print(f"   • Response Actions: {cursor.fetchone()[0]}")
        cursor.execute("SELECT COUNT(*) FROM vulnerabilities")
        print(f"   • Vulnerabilities: {cursor.fetchone()[0]}")
        cursor.execute("SELECT COUNT(*) FROM indicators_of_compromise")
        print(f"   • IoCs: {cursor.fetchone()[0]}")
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
        sys.exit(1)
    
    success = test_realistic_scenarios(db_path)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
