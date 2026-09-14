#!/usr/bin/env python3
"""
Security Events Generator
Генерирует синтетические security events (логи безопасности)
"""

import random
import json
from datetime import datetime, timedelta


def generate_failed_login_event(source_ip, target_ip, username=None):
    """Генерирует failed login event"""
    usernames = ['root', 'admin', 'administrator', 'user', 'test', 'guest', 'postgres', 'mysql']
    
    return {
        'source_system': 'auth',
        'source_ip': source_ip,
        'destination_ip': target_ip,
        'event_type': 'failed_login',
        'event_category': 'authentication',
        'severity': 'medium',
        'event_description': f'Failed login attempt for user {username or random.choice(usernames)}',
        'username': username or random.choice(usernames),
        'protocol': 'SSH',
        'action_taken': 'logged',
        'raw_log': f"Failed password for {username or 'root'} from {source_ip} port 22 ssh2"
    }


def generate_port_scan_event(source_ip, target_ip):
    """Генерирует port scan detection event"""
    ports_scanned = random.randint(50, 500)
    
    return {
        'source_system': 'ids',
        'source_ip': source_ip,
        'destination_ip': target_ip,
        'event_type': 'port_scan',
        'event_category': 'network',
        'severity': 'high',
        'event_description': f'Port scan detected: {ports_scanned} ports scanned',
        'protocol': 'TCP',
        'action_taken': 'alerted',
        'parsed_data': json.dumps({
            'ports_scanned': ports_scanned,
            'scan_type': random.choice(['SYN', 'ACK', 'XMAS', 'NULL']),
            'duration_seconds': random.randint(10, 300)
        }),
        'raw_log': f"[IDS] Port scan from {source_ip} targeting {target_ip}"
    }


def generate_malware_detected_event(asset_id, target_ip):
    """Генерирует malware detection event"""
    malware_families = ['Emotet', 'TrickBot', 'Dridex', 'Qakbot', 'CobaltStrike', 'Mimikatz']
    malware = random.choice(malware_families)
    
    file_paths = [
        'C:\\Users\\user\\Downloads\\invoice.doc',
        'C:\\Windows\\Temp\\update.exe',
        '/tmp/payload.sh',
        '/var/www/html/upload.php',
        'C:\\Program Files\\app\\malicious.dll'
    ]
    
    return {
        'source_system': 'endpoint_protection',
        'destination_ip': target_ip,
        'source_asset_id': asset_id,
        'event_type': 'malware_detected',
        'event_category': 'malware',
        'severity': 'critical',
        'event_description': f'{malware} malware detected and quarantined',
        'action_taken': 'quarantined',
        'parsed_data': json.dumps({
            'malware_family': malware,
            'file_path': random.choice(file_paths),
            'hash_md5': ''.join(random.choices('0123456789abcdef', k=32)),
            'action': 'quarantined'
        }),
        'raw_log': f"[AV] {malware} detected in file, action: quarantine"
    }


def generate_firewall_block_event(source_ip, target_ip):
    """Генерирует firewall block event"""
    reasons = [
        'Blacklisted IP',
        'Policy violation',
        'Suspicious traffic pattern',
        'Geo-blocking rule',
        'Rate limit exceeded'
    ]
    
    return {
        'source_system': 'firewall',
        'source_ip': source_ip,
        'destination_ip': target_ip,
        'destination_port': random.choice([80, 443, 22, 3389, 3306, 5432]),
        'event_type': 'firewall_block',
        'event_category': 'network',
        'severity': 'medium',
        'event_description': f'Connection blocked: {random.choice(reasons)}',
        'protocol': random.choice(['TCP', 'UDP']),
        'action_taken': 'blocked',
        'raw_log': f"[FW] BLOCKED {source_ip} -> {target_ip}"
    }


def generate_sql_injection_attempt(source_ip, target_ip):
    """Генерирует SQL injection attempt event"""
    sql_patterns = [
        "' OR '1'='1",
        "'; DROP TABLE users--",
        "' UNION SELECT * FROM passwords--",
        "admin'--",
        "1' AND 1=1--"
    ]
    
    return {
        'source_system': 'waf',
        'source_ip': source_ip,
        'destination_ip': target_ip,
        'destination_port': 443,
        'event_type': 'sql_injection_attempt',
        'event_category': 'application',
        'severity': 'high',
        'event_description': 'SQL injection attempt detected in HTTP request',
        'protocol': 'HTTPS',
        'action_taken': 'blocked',
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'parsed_data': json.dumps({
            'attack_pattern': random.choice(sql_patterns),
            'url': f'/login.php?user=admin&password={random.choice(sql_patterns)}'
        }),
        'raw_log': f"[WAF] SQL injection blocked from {source_ip}"
    }


def generate_privilege_escalation_event(asset_id, target_ip, username):
    """Генерирует privilege escalation attempt event"""
    return {
        'source_system': 'system',
        'destination_ip': target_ip,
        'source_asset_id': asset_id,
        'event_type': 'privilege_escalation_attempt',
        'event_category': 'system',
        'severity': 'high',
        'event_description': f'User {username} attempted privilege escalation',
        'username': username,
        'action_taken': 'blocked',
        'parsed_data': json.dumps({
            'method': random.choice(['sudo', 'setuid', 'exploit']),
            'target_privilege': 'root'
        }),
        'raw_log': f"[SYSTEM] Privilege escalation attempt by {username}"
    }


def generate_data_exfiltration_event(source_ip, target_ip, asset_id):
    """Генерирует data exfiltration detection event"""
    data_size_mb = random.randint(100, 5000)
    
    return {
        'source_system': 'dlp',
        'source_ip': source_ip,
        'destination_ip': target_ip,
        'source_asset_id': asset_id,
        'event_type': 'data_exfiltration',
        'event_category': 'data_access',
        'severity': 'critical',
        'event_description': f'Large data transfer detected: {data_size_mb}MB',
        'protocol': random.choice(['FTP', 'HTTPS', 'SMB']),
        'action_taken': 'alerted',
        'parsed_data': json.dumps({
            'data_size_mb': data_size_mb,
            'file_count': random.randint(10, 100),
            'contains_pii': random.choice([True, False])
        }),
        'raw_log': f"[DLP] Large data transfer from {source_ip} to {target_ip}"
    }


def generate_suspicious_process_event(asset_id, target_ip):
    """Генерирует suspicious process execution event"""
    suspicious_processes = [
        'powershell.exe -enc',
        'cmd.exe /c whoami',
        'nc.exe -e cmd.exe',
        'mimikatz.exe',
        'psexec.exe'
    ]
    
    return {
        'source_system': 'edr',
        'destination_ip': target_ip,
        'source_asset_id': asset_id,
        'event_type': 'suspicious_process',
        'event_category': 'system',
        'severity': 'high',
        'event_description': 'Suspicious process execution detected',
        'action_taken': 'terminated',
        'parsed_data': json.dumps({
            'process_name': random.choice(suspicious_processes),
            'parent_process': random.choice(['explorer.exe', 'winword.exe', 'outlook.exe']),
            'command_line': random.choice(suspicious_processes)
        }),
        'raw_log': f"[EDR] Suspicious process detected and terminated"
    }


def generate_unauthorized_access_event(source_ip, target_ip, asset_id):
    """Генерирует unauthorized access attempt event"""
    resources = [
        '/admin/dashboard',
        '/api/users',
        '/config/database.yml',
        'C:\\Windows\\System32\\config',
        '/etc/shadow'
    ]
    
    return {
        'source_system': 'access_control',
        'source_ip': source_ip,
        'destination_ip': target_ip,
        'source_asset_id': asset_id,
        'event_type': 'unauthorized_access',
        'event_category': 'policy_violation',
        'severity': 'high',
        'event_description': f'Unauthorized access attempt to restricted resource',
        'action_taken': 'blocked',
        'parsed_data': json.dumps({
            'resource': random.choice(resources),
            'required_permission': 'admin',
            'user_permission': 'user'
        }),
        'raw_log': f"[ACCESS] Unauthorized access blocked from {source_ip}"
    }


def generate_security_events(count=500, assets_count=50):
    """
    Генерирует security events
    
    Args:
        count: количество events
        assets_count: количество assets (для привязки)
        
    Returns:
        list of dict: список events
    """
    
    events = []
    
    # Event types distribution
    event_generators = {
        generate_failed_login_event: 0.25,
        generate_port_scan_event: 0.15,
        generate_malware_detected_event: 0.10,
        generate_firewall_block_event: 0.20,
        generate_sql_injection_attempt: 0.10,
        generate_privilege_escalation_event: 0.05,
        generate_data_exfiltration_event: 0.05,
        generate_suspicious_process_event: 0.05,
        generate_unauthorized_access_event: 0.05
    }
    
    # Generate realistic IPs
    internal_ips = [f"192.168.{random.randint(1,254)}.{random.randint(1,254)}" for _ in range(50)]
    external_ips = [
        f"45.142.{random.randint(1,254)}.{random.randint(1,254)}",
        f"185.220.{random.randint(1,254)}.{random.randint(1,254)}",
        f"91.109.{random.randint(1,254)}.{random.randint(1,254)}"
    ] * 10
    
    usernames = ['john.doe', 'jane.smith', 'bob.wilson', 'alice.brown', 'admin', 'root']
    
    # Generate events over last 30 days
    now = datetime.now()
    
    for i in range(count):
        # Select event type
        generator = random.choices(
            list(event_generators.keys()),
            weights=list(event_generators.values())
        )[0]
        
        # Generate timestamp (распределено по последним 30 дням)
        days_ago = random.randint(0, 30)
        hours_ago = random.randint(0, 23)
        minutes_ago = random.randint(0, 59)
        event_timestamp = now - timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago)
        
        # Generate base parameters
        source_ip = random.choice(external_ips if random.random() < 0.3 else internal_ips)
        target_ip = random.choice(internal_ips)
        asset_id = random.randint(1, assets_count)
        username = random.choice(usernames)
        
        # Generate event
        if generator == generate_failed_login_event:
            event = generator(source_ip, target_ip, username)
        elif generator in [generate_malware_detected_event, generate_suspicious_process_event]:
            event = generator(asset_id, target_ip)
        elif generator == generate_privilege_escalation_event:
            event = generator(asset_id, target_ip, username)
        elif generator == generate_data_exfiltration_event:
            event = generator(source_ip, random.choice(external_ips), asset_id)
        elif generator == generate_unauthorized_access_event:
            event = generator(source_ip, target_ip, asset_id)
        else:
            event = generator(source_ip, target_ip)
        
        # Add common fields
        event['event_timestamp'] = event_timestamp.isoformat()
        event['processed'] = 0
        event['false_positive'] = 0
        
        # Tags
        tags = [event['event_category'], event['severity']]
        if event['severity'] in ['critical', 'high']:
            tags.append('priority')
        event['tags'] = json.dumps(tags)
        
        # Metadata
        event['metadata'] = json.dumps({
            'event_id': i + 1,
            'collector': event['source_system'],
            'timestamp_received': now.isoformat()
        })
        
        events.append(event)
    
    # Sort by timestamp
    events.sort(key=lambda x: x['event_timestamp'])
    
    return events


def save_to_json(events, filename='data/samples/security_events.json'):
    """Сохраняет events в JSON файл"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(events, f, indent=2, ensure_ascii=False)
    print(f"Generated {len(events)} security events")
    print(f"Saved to: {filename}")


def save_to_sql(events, filename='data/samples/security_events.sql'):
    """Сохраняет events в SQL INSERT statements"""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("-- Generated Security Events Data\n")
        f.write("-- Generated at: {}\n\n".format(datetime.now().isoformat()))
        
        for event in events:
            f.write("INSERT INTO security_events (")
            
            fields = [
                'event_timestamp', 'source_system', 'source_ip', 'source_port',
                'source_asset_id', 'destination_ip', 'destination_port', 'destination_asset_id',
                'event_type', 'event_category', 'severity', 'event_description',
                'raw_log', 'parsed_data', 'username', 'user_agent',
                'protocol', 'action_taken', 'processed', 'false_positive',
                'tags', 'metadata'
            ]
            
            f.write(", ".join(fields))
            f.write(") VALUES (")
            
            values = []
            for field in fields:
                value = event.get(field)
                if value is None:
                    values.append("NULL")
                elif isinstance(value, (int, bool)):
                    values.append(str(value))
                else:
                    values.append(f"'{value}'")
            
            f.write(", ".join(values))
            f.write(");\n")
    
    print(f"Saved SQL to: {filename}")


def print_summary(events):
    """Выводит статистику по сгенерированным events"""
    print("\nSecurity Events Summary:")
    print("-" * 50)
    
    print(f"Total: {len(events)}")
    
    # По категориям
    categories = {}
    for event in events:
        cat = event['event_category']
        categories[cat] = categories.get(cat, 0) + 1
    
    print("\nBy Category:")
    for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        print(f"  {cat}: {count}")
    
    # По severity
    severity = {}
    for event in events:
        sev = event['severity']
        severity[sev] = severity.get(sev, 0) + 1
    
    print("\nBy Severity:")
    for sev, count in sorted(severity.items(), key=lambda x: ['critical', 'high', 'medium', 'low', 'info'].index(x[0])):
        print(f"  {sev}: {count}")
    
    # Top event types
    types = {}
    for event in events:
        et = event['event_type']
        types[et] = types.get(et, 0) + 1
    
    print("\nTop Event Types:")
    for et, count in sorted(types.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  {et}: {count}")
    
    # Timeline
    first = min(e['event_timestamp'] for e in events)
    last = max(e['event_timestamp'] for e in events)
    print(f"\nTimeline:")
    print(f"  First event: {first}")
    print(f"  Last event: {last}")


if __name__ == "__main__":
    # Генерируем 500 events
    events = generate_security_events(count=500, assets_count=50)
    
    # Сохраняем
    save_to_json(events)
    save_to_sql(events)
    
    # Выводим статистику
    print_summary(events)
    
    print("\nDone!")
