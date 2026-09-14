#!/usr/bin/env python3
"""
IoC Generator
Генерирует Indicators of Compromise (malicious IPs, domains, hashes)
"""

import random
import json
import hashlib
from datetime import datetime, timedelta


def generate_malicious_ip():
    """Генерирует реалистичный malicious IP"""
    # Известные bad ranges
    bad_ranges = [
        '45.142.',  # Russia/Ukraine
        '185.220.',  # TOR exit nodes
        '91.109.',   # Russia
        '103.253.',  # Asia suspicious
        '194.67.',   # Russia
        '23.95.',    # US hosting
    ]
    
    prefix = random.choice(bad_ranges)
    return f"{prefix}{random.randint(1, 254)}.{random.randint(1, 254)}"


def generate_malicious_domain():
    """Генерирует suspicious domain"""
    tlds = ['.ru', '.cn', '.tk', '.ml', '.ga', '.cf', '.xyz', '.top']
    
    patterns = [
        'secure-login',
        'verify-account',
        'update-payment',
        'confirm-identity',
        'banking-secure',
        'paypal-verify',
        'microsoft-update',
        'apple-support',
        'amazon-secure',
        'google-verify'
    ]
    
    pattern = random.choice(patterns)
    number = random.randint(1, 999)
    tld = random.choice(tlds)
    
    return f"{pattern}{number}{tld}"


def generate_file_hash():
    """Генерирует случайный file hash"""
    random_string = f"{random.random()}{datetime.now().isoformat()}"
    return hashlib.md5(random_string.encode()).hexdigest()


def generate_malware_name():
    """Генерирует название malware"""
    families = [
        'Emotet', 'TrickBot', 'Dridex', 'Qakbot', 'IcedID',
        'Ryuk', 'Conti', 'LockBit', 'BlackCat', 'REvil',
        'CobaltStrike', 'Mimikatz', 'BloodHound', 'SharpHound',
        'AsyncRAT', 'NanoCore', 'QuasarRAT', 'DarkComet'
    ]
    return random.choice(families)


def generate_attack_pattern():
    """Генерирует MITRE ATT&CK pattern"""
    tactics = [
        'Initial Access', 'Execution', 'Persistence', 'Privilege Escalation',
        'Defense Evasion', 'Credential Access', 'Discovery', 'Lateral Movement',
        'Collection', 'Command and Control', 'Exfiltration', 'Impact'
    ]
    
    techniques = {
        'Initial Access': ['T1078', 'T1190', 'T1133', 'T1566'],
        'Execution': ['T1059', 'T1204', 'T1047', 'T1053'],
        'Persistence': ['T1053', 'T1136', 'T1098', 'T1547'],
        'Credential Access': ['T1110', 'T1555', 'T1056', 'T1003'],
        'Command and Control': ['T1071', 'T1573', 'T1090', 'T1095']
    }
    
    tactic = random.choice(list(techniques.keys()))
    technique = random.choice(techniques[tactic])
    
    return f"{tactic} - {technique}"


def generate_iocs(count=100):
    """
    Генерирует IoC данные
    
    Args:
        count: количество IoC
        
    Returns:
        list of dict: список IoC
    """
    
    iocs = []
    
    # IoC type distribution
    ioc_types = {
        'ip_address': 0.4,
        'domain': 0.3,
        'file_hash': 0.25,
        'url': 0.05
    }
    
    # Threat types
    threat_types = [
        'malware', 'phishing', 'c2', 'botnet', 'ransomware',
        'trojan', 'backdoor', 'spyware', 'adware', 'exploit'
    ]
    
    # Sources
    sources = [
        'VirusTotal', 'AbuseIPDB', 'AlienVault OTX', 'Threat Fox',
        'URLhaus', 'MalwareBazaar', 'Internal Detection', 'OSINT'
    ]
    
    for i in range(count):
        # Выбираем тип IoC
        ioc_type = random.choices(
            list(ioc_types.keys()),
            weights=list(ioc_types.values())
        )[0]
        
        # Генерируем значение
        if ioc_type == 'ip_address':
            ioc_value = generate_malicious_ip()
            hash_type = None
        elif ioc_type == 'domain':
            ioc_value = generate_malicious_domain()
            hash_type = None
        elif ioc_type == 'file_hash':
            ioc_value = generate_file_hash()
            hash_type = random.choice(['MD5', 'SHA1', 'SHA256'])
        else:  # url
            domain = generate_malicious_domain()
            path = random.choice(['/login', '/update', '/verify', '/download', '/secure'])
            ioc_value = f"http://{domain}{path}"
            hash_type = None
        
        # Threat type и malware family
        threat_type = random.choice(threat_types)
        malware_family = generate_malware_name() if threat_type in ['malware', 'ransomware', 'trojan'] else None
        
        # Severity
        severity = random.choices(
            ['critical', 'high', 'medium', 'low'],
            weights=[0.2, 0.3, 0.3, 0.2]
        )[0]
        
        # Confidence score
        if threat_type in ['malware', 'ransomware']:
            confidence = random.randint(80, 100)
        else:
            confidence = random.randint(60, 95)
        
        # Source
        source = random.choice(sources)
        
        # Dates
        first_seen_days = random.randint(1, 365)
        first_seen = (datetime.now() - timedelta(days=first_seen_days)).strftime('%Y-%m-%d')
        
        last_seen_days = random.randint(0, first_seen_days)
        last_seen = (datetime.now() - timedelta(days=last_seen_days)).strftime('%Y-%m-%d')
        
        # Expires (через 30-90 дней)
        expires_days = random.randint(30, 90)
        expires_at = (datetime.now() + timedelta(days=expires_days)).strftime('%Y-%m-%d')
        
        # Description
        descriptions = {
            'ip_address': f"Known {threat_type} C2 server",
            'domain': f"Phishing domain impersonating legitimate service",
            'file_hash': f"{malware_family} malware sample" if malware_family else f"{threat_type} sample",
            'url': f"Malicious URL hosting {threat_type} payload"
        }
        
        description = descriptions.get(ioc_type, f"{threat_type} indicator")
        
        # Attack pattern
        attack_pattern = generate_attack_pattern()
        
        # Is active
        is_active = random.choice([True, True, True, False])  # 75% active
        
        # Tags
        tags = [threat_type, ioc_type]
        if malware_family:
            tags.append(malware_family)
        if severity in ['critical', 'high']:
            tags.append('priority')
        
        ioc = {
            'ioc_type': ioc_type,
            'ioc_value': ioc_value,
            'hash_type': hash_type,
            'threat_type': threat_type,
            'malware_family': malware_family,
            'severity': severity,
            'confidence_score': confidence,
            'source': source,
            'source_url': f"https://{source.lower().replace(' ', '')}.com/indicator/{i+1}",
            'first_seen': first_seen,
            'last_seen': last_seen,
            'expires_at': expires_at,
            'description': description,
            'attack_pattern': attack_pattern,
            'is_active': 1 if is_active else 0,
            'false_positive': 0,
            'tags': json.dumps(tags),
            'metadata': json.dumps({
                'detection_count': random.randint(1, 100),
                'reports': random.randint(1, 50)
            })
        }
        
        iocs.append(ioc)
    
    return iocs


def save_to_json(iocs, filename='data/samples/ioc.json'):
    """Сохраняет IoC в JSON файл"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(iocs, f, indent=2, ensure_ascii=False)
    print(f"Generated {len(iocs)} IoCs")
    print(f"Saved to: {filename}")


def save_to_sql(iocs, filename='data/samples/ioc.sql'):
    """Сохраняет IoC в SQL INSERT statements"""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("-- Generated IoC Data\n")
        f.write("-- Generated at: {}\n\n".format(datetime.now().isoformat()))
        
        for ioc in iocs:
            f.write("INSERT INTO indicators_of_compromise (")
            f.write("ioc_type, ioc_value, hash_type, threat_type, malware_family, ")
            f.write("severity, confidence_score, source, source_url, ")
            f.write("first_seen, last_seen, expires_at, description, attack_pattern, ")
            f.write("is_active, false_positive, tags, metadata")
            f.write(") VALUES (")
            
            values = [
                f"'{ioc['ioc_type']}'",
                f"'{ioc['ioc_value']}'",
                f"'{ioc['hash_type']}'" if ioc['hash_type'] else "NULL",
                f"'{ioc['threat_type']}'",
                f"'{ioc['malware_family']}'" if ioc['malware_family'] else "NULL",
                f"'{ioc['severity']}'",
                str(ioc['confidence_score']),
                f"'{ioc['source']}'",
                f"'{ioc['source_url']}'",
                f"'{ioc['first_seen']}'",
                f"'{ioc['last_seen']}'",
                f"'{ioc['expires_at']}'",
                f"'{ioc['description']}'",
                f"'{ioc['attack_pattern']}'",
                str(ioc['is_active']),
                str(ioc['false_positive']),
                f"'{ioc['tags']}'",
                f"'{ioc['metadata']}'"
            ]
            
            f.write(", ".join(values))
            f.write(");\n")
    
    print(f"Saved SQL to: {filename}")


def print_summary(iocs):
    """Выводит статистику по сгенерированным IoC"""
    print("\nIoC Summary:")
    print("-" * 50)
    
    # По типам
    types = {}
    for ioc in iocs:
        ioc_type = ioc['ioc_type']
        types[ioc_type] = types.get(ioc_type, 0) + 1
    
    print("By Type:")
    for ioc_type, count in sorted(types.items()):
        print(f"  {ioc_type}: {count}")
    
    # По threat type
    threats = {}
    for ioc in iocs:
        threat = ioc['threat_type']
        threats[threat] = threats.get(threat, 0) + 1
    
    print("\nBy Threat Type:")
    for threat, count in sorted(threats.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  {threat}: {count}")
    
    # По severity
    severity = {}
    for ioc in iocs:
        sev = ioc['severity']
        severity[sev] = severity.get(sev, 0) + 1
    
    print("\nBy Severity:")
    for sev, count in sorted(severity.items(), key=lambda x: ['critical', 'high', 'medium', 'low'].index(x[0])):
        print(f"  {sev}: {count}")
    
    # Active vs inactive
    active = sum(1 for ioc in iocs if ioc['is_active'])
    print(f"\nActive: {active} / {len(iocs)} ({active/len(iocs)*100:.1f}%)")


if __name__ == "__main__":
    # Генерируем 100 IoCs
    iocs = generate_iocs(count=100)
    
    # Сохраняем
    save_to_json(iocs)
    save_to_sql(iocs)
    
    # Выводим статистику
    print_summary(iocs)
    
    print("\nDone!")
