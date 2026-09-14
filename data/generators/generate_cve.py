#!/usr/bin/env python3
"""
CVE/Vulnerabilities Generator
Генерирует тестовые данные уязвимостей на assets
"""

import random
import json
from datetime import datetime, timedelta


# Известные CVE для реалистичности
KNOWN_CVES = [
    {
        'cve_id': 'CVE-2021-44228',
        'name': 'Apache Log4j2 Remote Code Execution (Log4Shell)',
        'cvss': 10.0,
        'type': 'RCE',
        'software': 'Apache Log4j',
        'versions': ['2.0-beta9', '2.14.1'],
        'patch': '2.17.0',
        'description': 'Remote code execution via JNDI injection'
    },
    {
        'cve_id': 'CVE-2021-45046',
        'name': 'Apache Log4j2 DoS Vulnerability',
        'cvss': 9.0,
        'type': 'DoS',
        'software': 'Apache Log4j',
        'versions': ['2.0-beta9', '2.16.0'],
        'patch': '2.17.0',
        'description': 'Denial of Service via crafted input'
    },
    {
        'cve_id': 'CVE-2022-22965',
        'name': 'Spring4Shell - Spring Framework RCE',
        'cvss': 9.8,
        'type': 'RCE',
        'software': 'Spring Framework',
        'versions': ['5.3.0', '5.3.17'],
        'patch': '5.3.18',
        'description': 'Remote code execution in Spring Framework'
    },
    {
        'cve_id': 'CVE-2022-0847',
        'name': 'Dirty Pipe - Linux Kernel Privilege Escalation',
        'cvss': 7.8,
        'type': 'Privilege Escalation',
        'software': 'Linux Kernel',
        'versions': ['5.8', '5.16.10'],
        'patch': '5.16.11',
        'description': 'Local privilege escalation vulnerability'
    },
    {
        'cve_id': 'CVE-2021-3156',
        'name': 'Sudo Heap-Based Buffer Overflow (Baron Samedit)',
        'cvss': 7.8,
        'type': 'Privilege Escalation',
        'software': 'Sudo',
        'versions': ['1.8.2', '1.8.31p2'],
        'patch': '1.9.5p2',
        'description': 'Heap-based buffer overflow in sudo'
    },
    {
        'cve_id': 'CVE-2020-1472',
        'name': 'Zerologon - Netlogon Elevation of Privilege',
        'cvss': 10.0,
        'type': 'Privilege Escalation',
        'software': 'Windows Netlogon',
        'versions': ['Windows Server 2008 R2', 'Windows Server 2019'],
        'patch': 'KB4571694',
        'description': 'Netlogon elevation of privilege vulnerability'
    },
    {
        'cve_id': 'CVE-2019-0708',
        'name': 'BlueKeep - RDP Remote Code Execution',
        'cvss': 9.8,
        'type': 'RCE',
        'software': 'Windows RDP',
        'versions': ['Windows 7', 'Windows Server 2008'],
        'patch': 'KB4499175',
        'description': 'Remote Desktop Services RCE vulnerability'
    },
    {
        'cve_id': 'CVE-2017-0144',
        'name': 'EternalBlue - SMBv1 Remote Code Execution',
        'cvss': 8.1,
        'type': 'RCE',
        'software': 'Windows SMB',
        'versions': ['Windows XP', 'Windows 10'],
        'patch': 'MS17-010',
        'description': 'SMBv1 remote code execution'
    }
]


def generate_cve_vulnerabilities(assets_count=50, vuln_per_asset_max=3):
    """
    Генерирует уязвимости для assets
    
    Args:
        assets_count: количество assets (должно совпадать с generate_assets)
        vuln_per_asset_max: максимум уязвимостей на asset
        
    Returns:
        list of dict: список vulnerabilities
    """
    
    vulnerabilities = []
    
    # Статусы
    statuses = ['open', 'in_progress', 'patched', 'mitigated', 'accepted_risk']
    status_weights = [0.4, 0.2, 0.25, 0.1, 0.05]
    
    # Приоритеты
    priorities = ['critical', 'high', 'medium', 'low']
    
    # Scanners
    scanners = ['Nessus', 'OpenVAS', 'Qualys', 'Nexpose', 'Burp Suite', 'Manual Audit']
    
    for asset_id in range(1, assets_count + 1):
        # Не все assets имеют уязвимости
        if random.random() < 0.3:  # 30% без уязвимостей
            continue
        
        # Сколько уязвимостей на этом asset
        vuln_count = random.randint(1, vuln_per_asset_max)
        
        for _ in range(vuln_count):
            # Выбираем CVE
            cve_data = random.choice(KNOWN_CVES)
            
            # CVSS score (может отличаться от базового)
            base_cvss = cve_data['cvss']
            cvss_score = round(base_cvss + random.uniform(-0.5, 0.5), 1)
            cvss_score = max(0.0, min(10.0, cvss_score))  # Clamp 0-10
            
            # Severity based on CVSS
            if cvss_score >= 9.0:
                severity = 'critical'
            elif cvss_score >= 7.0:
                severity = 'high'
            elif cvss_score >= 4.0:
                severity = 'medium'
            else:
                severity = 'low'
            
            # CVSS vector
            cvss_vectors = [
                'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H',
                'CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H',
                'CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H',
                'CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N'
            ]
            cvss_vector = random.choice(cvss_vectors)
            
            # Exploit available
            exploit_available = severity in ['critical', 'high'] and random.random() < 0.6
            exploit_public = exploit_available and random.random() < 0.7
            actively_exploited = exploit_public and random.random() < 0.3
            
            # Patch available
            patch_available = random.random() < 0.8
            
            # Status
            if patch_available:
                status = random.choices(statuses, weights=status_weights)[0]
            else:
                status = random.choice(['open', 'mitigated', 'accepted_risk'])
            
            # Priority
            if actively_exploited:
                priority = 'critical'
            elif severity == 'critical':
                priority = random.choice(['critical', 'critical', 'high'])
            elif severity == 'high':
                priority = random.choice(['high', 'high', 'medium'])
            else:
                priority = random.choice(['medium', 'low'])
            
            # Dates
            scan_days_ago = random.randint(0, 30)
            scan_date = (datetime.now() - timedelta(days=scan_days_ago)).strftime('%Y-%m-%d')
            
            discovered_days_ago = random.randint(scan_days_ago, scan_days_ago + 90)
            discovered_at = (datetime.now() - timedelta(days=discovered_days_ago)).strftime('%Y-%m-%d')
            
            # Due date (SLA based on priority)
            sla_days = {
                'critical': 7,
                'high': 30,
                'medium': 90,
                'low': 180
            }
            due_days = sla_days.get(priority, 90)
            due_date = (datetime.now() + timedelta(days=due_days)).strftime('%Y-%m-%d')
            
            # Resolved date (если patched)
            resolved_at = None
            if status == 'patched':
                resolved_days_ago = random.randint(0, discovered_days_ago)
                resolved_at = (datetime.now() - timedelta(days=resolved_days_ago)).strftime('%Y-%m-%d')
            
            # Verified date
            verified_at = resolved_at if resolved_at else None
            
            # Assignment
            assigned_teams = ['DevOps Team', 'Security Team', 'Infrastructure Team', 'Development Team']
            assigned_team = random.choice(assigned_teams)
            
            assigned_to = random.choice([
                'John Smith', 'Jane Doe', 'Bob Wilson', 'Alice Brown',
                'Charlie Davis', 'Emma Johnson', None
            ])
            
            # Remediation steps
            remediation_steps = f"1. Update {cve_data['software']} to version {cve_data['patch']}\n"
            remediation_steps += "2. Verify the update was successful\n"
            remediation_steps += "3. Restart affected services\n"
            remediation_steps += "4. Re-scan to confirm remediation"
            
            # Workaround
            workarounds = [
                "Disable affected service until patch is applied",
                "Apply network segmentation to limit exposure",
                "Enable additional logging and monitoring",
                "Implement compensating controls via firewall rules",
                None
            ]
            workaround = random.choice(workarounds)
            
            # Scanner
            scanner_name = random.choice(scanners)
            
            # CVE published date
            cve_year = int(cve_data['cve_id'].split('-')[1])
            cve_published = f"{cve_year}-{random.randint(1,12):02d}-{random.randint(1,28):02d}"
            
            # Affected version (random from known versions)
            affected_version = random.choice(cve_data['versions'])
            
            vulnerability = {
                'cve_id': cve_data['cve_id'],
                'cve_published_date': cve_published,
                'asset_id': asset_id,
                'vulnerability_name': cve_data['name'],
                'description': cve_data['description'],
                'cvss_score': cvss_score,
                'cvss_vector': cvss_vector,
                'severity': severity,
                'vulnerability_type': cve_data['type'],
                'category': cve_data['type'],
                'affected_software': cve_data['software'],
                'affected_version': affected_version,
                'exploit_available': 1 if exploit_available else 0,
                'exploit_public': 1 if exploit_public else 0,
                'actively_exploited': 1 if actively_exploited else 0,
                'patch_available': 1 if patch_available else 0,
                'patch_version': cve_data['patch'] if patch_available else None,
                'remediation_steps': remediation_steps,
                'workaround': workaround,
                'status': status,
                'priority': priority,
                'due_date': due_date,
                'assigned_to': assigned_to,
                'assigned_team': assigned_team,
                'scan_date': scan_date,
                'scanner_name': scanner_name,
                'discovered_at': discovered_at,
                'resolved_at': resolved_at,
                'verified_at': verified_at,
                'tags': json.dumps([severity, cve_data['type'], cve_data['software'].split()[0]]),
                'metadata': json.dumps({
                    'references': [
                        f"https://nvd.nist.gov/vuln/detail/{cve_data['cve_id']}",
                        f"https://cve.mitre.org/cgi-bin/cvename.cgi?name={cve_data['cve_id']}"
                    ],
                    'exploit_db': f"https://www.exploit-db.com/search?cve={cve_data['cve_id']}" if exploit_available else None
                })
            }
            
            vulnerabilities.append(vulnerability)
    
    return vulnerabilities


def save_to_json(vulnerabilities, filename='data/samples/vulnerabilities.json'):
    """Сохраняет vulnerabilities в JSON файл"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(vulnerabilities, f, indent=2, ensure_ascii=False)
    print(f"Generated {len(vulnerabilities)} vulnerabilities")
    print(f"Saved to: {filename}")


def save_to_sql(vulnerabilities, filename='data/samples/vulnerabilities.sql'):
    """Сохраняет vulnerabilities в SQL INSERT statements"""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("-- Generated Vulnerabilities Data\n")
        f.write("-- Generated at: {}\n\n".format(datetime.now().isoformat()))
        
        for vuln in vulnerabilities:
            f.write("INSERT INTO vulnerabilities (")
            f.write("cve_id, cve_published_date, asset_id, vulnerability_name, description, ")
            f.write("cvss_score, cvss_vector, severity, vulnerability_type, category, ")
            f.write("affected_software, affected_version, exploit_available, exploit_public, ")
            f.write("actively_exploited, patch_available, patch_version, remediation_steps, ")
            f.write("workaround, status, priority, due_date, assigned_to, assigned_team, ")
            f.write("scan_date, scanner_name, discovered_at, resolved_at, verified_at, tags, metadata")
            f.write(") VALUES (")
            
            values = [
                f"'{vuln['cve_id']}'",
                f"'{vuln['cve_published_date']}'",
                str(vuln['asset_id']),
                f"'{vuln['vulnerability_name']}'",
                f"'{vuln['description']}'",
                str(vuln['cvss_score']),
                f"'{vuln['cvss_vector']}'",
                f"'{vuln['severity']}'",
                f"'{vuln['vulnerability_type']}'",
                f"'{vuln['category']}'",
                f"'{vuln['affected_software']}'",
                f"'{vuln['affected_version']}'",
                str(vuln['exploit_available']),
                str(vuln['exploit_public']),
                str(vuln['actively_exploited']),
                str(vuln['patch_available']),
                f"'{vuln['patch_version']}'" if vuln['patch_version'] else "NULL",
                f"'{vuln['remediation_steps']}'",
                f"'{vuln['workaround']}'" if vuln['workaround'] else "NULL",
                f"'{vuln['status']}'",
                f"'{vuln['priority']}'",
                f"'{vuln['due_date']}'",
                f"'{vuln['assigned_to']}'" if vuln['assigned_to'] else "NULL",
                f"'{vuln['assigned_team']}'",
                f"'{vuln['scan_date']}'",
                f"'{vuln['scanner_name']}'",
                f"'{vuln['discovered_at']}'",
                f"'{vuln['resolved_at']}'" if vuln['resolved_at'] else "NULL",
                f"'{vuln['verified_at']}'" if vuln['verified_at'] else "NULL",
                f"'{vuln['tags']}'",
                f"'{vuln['metadata']}'"
            ]
            
            f.write(", ".join(values))
            f.write(");\n")
    
    print(f"Saved SQL to: {filename}")


def print_summary(vulnerabilities):
    """Выводит статистику по сгенерированным vulnerabilities"""
    print("\nVulnerabilities Summary:")
    print("-" * 50)
    
    print(f"Total: {len(vulnerabilities)}")
    
    # По severity
    severity = {}
    for vuln in vulnerabilities:
        sev = vuln['severity']
        severity[sev] = severity.get(sev, 0) + 1
    
    print("\nBy Severity:")
    for sev, count in sorted(severity.items(), key=lambda x: ['critical', 'high', 'medium', 'low'].index(x[0])):
        print(f"  {sev}: {count}")
    
    # По status
    status = {}
    for vuln in vulnerabilities:
        st = vuln['status']
        status[st] = status.get(st, 0) + 1
    
    print("\nBy Status:")
    for st, count in sorted(status.items(), key=lambda x: x[1], reverse=True):
        print(f"  {st}: {count}")
    
    # CVE distribution
    cves = {}
    for vuln in vulnerabilities:
        cve = vuln['cve_id']
        cves[cve] = cves.get(cve, 0) + 1
    
    print("\nTop CVEs:")
    for cve, count in sorted(cves.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  {cve}: {count} assets")
    
    # Exploit stats
    with_exploit = sum(1 for v in vulnerabilities if v['exploit_available'])
    actively = sum(1 for v in vulnerabilities if v['actively_exploited'])
    print(f"\nWith Public Exploit: {with_exploit} ({with_exploit/len(vulnerabilities)*100:.1f}%)")
    print(f"Actively Exploited: {actively} ({actively/len(vulnerabilities)*100:.1f}%)")


if __name__ == "__main__":
    # Генерируем vulnerabilities для 50 assets
    vulnerabilities = generate_cve_vulnerabilities(assets_count=50, vuln_per_asset_max=3)
    
    # Сохраняем
    save_to_json(vulnerabilities)
    save_to_sql(vulnerabilities)
    
    # Выводим статистику
    print_summary(vulnerabilities)
    
    print("\nDone!")
