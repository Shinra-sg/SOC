#!/usr/bin/env python3
"""
Mock Assets Generator
Генерирует тестовые данные для инфраструктуры (servers, workstations, devices)
"""

import random
import json
from datetime import datetime, timedelta


def generate_ip(subnet="192.168"):
    """Генерирует случайный IP адрес"""
    return f"{subnet}.{random.randint(1, 254)}.{random.randint(1, 254)}"


def generate_mac():
    """Генерирует случайный MAC адрес"""
    return ":".join([f"{random.randint(0, 255):02x}" for _ in range(6)])


def generate_assets(count=50):
    """
    Генерирует mock assets
    
    Args:
        count: количество assets
        
    Returns:
        list of dict: список assets
    """
    
    assets = []
    
    # Asset types distribution
    asset_types = {
        'server': 0.3,
        'workstation': 0.5,
        'network_device': 0.15,
        'mobile': 0.05
    }
    
    # Server names
    server_types = ['web', 'app', 'db', 'mail', 'file', 'backup', 'proxy', 'dns']
    
    # OS distributions
    server_os = [
        ('Ubuntu 22.04', 0.4),
        ('Ubuntu 20.04', 0.2),
        ('CentOS 8', 0.15),
        ('Debian 11', 0.15),
        ('Red Hat 8', 0.1)
    ]
    
    workstation_os = [
        ('Windows 10', 0.5),
        ('Windows 11', 0.3),
        ('macOS Ventura', 0.15),
        ('Ubuntu 22.04', 0.05)
    ]
    
    # Departments
    departments = ['IT', 'Finance', 'HR', 'Sales', 'Marketing', 'R&D', 'Support']
    
    # Locations
    locations = ['Office Floor 1', 'Office Floor 2', 'Office Floor 3', 'Data Center', 'Remote']
    
    # Users for workstations
    user_names = [
        'john.doe', 'jane.smith', 'bob.wilson', 'alice.brown', 'charlie.davis',
        'emma.johnson', 'oliver.williams', 'sophia.jones', 'liam.garcia', 'ava.martinez'
    ]
    
    asset_id = 1
    
    for _ in range(count):
        # Выбираем тип asset
        asset_type = random.choices(
            list(asset_types.keys()),
            weights=list(asset_types.values())
        )[0]
        
        # Генерируем базовую информацию
        ip_address = generate_ip()
        mac_address = generate_mac()
        
        if asset_type == 'server':
            server_type = random.choice(server_types)
            number = random.randint(1, 20)
            asset_name = f"{server_type}-server-{number:02d}"
            hostname = f"{server_type}{number:02d}.company.local"
            os_name, _ = random.choices(server_os, weights=[w for _, w in server_os])[0]
            criticality = random.choices(
                ['critical', 'high', 'medium', 'low'],
                weights=[0.3, 0.4, 0.2, 0.1]
            )[0]
            owner = 'IT Operations'
            department = 'IT'
            location = random.choice(['Data Center', 'Office Floor 1'])
            
        elif asset_type == 'workstation':
            department = random.choice(departments)
            user = random.choice(user_names)
            asset_name = f"ws-{department.lower()}-{random.randint(1, 50):02d}"
            hostname = f"{asset_name}.company.local"
            os_name, _ = random.choices(workstation_os, weights=[w for _, w in workstation_os])[0]
            criticality = random.choices(
                ['high', 'medium', 'low'],
                weights=[0.2, 0.5, 0.3]
            )[0]
            owner = user.replace('.', ' ').title()
            location = random.choice(locations[:4])  # No remote for workstations initially
            
        elif asset_type == 'network_device':
            device_types = ['switch', 'router', 'firewall', 'access-point']
            device_type = random.choice(device_types)
            number = random.randint(1, 10)
            asset_name = f"{device_type}-{number:02d}"
            hostname = f"{asset_name}.network.local"
            os_name = random.choice(['Cisco IOS', 'pfSense', 'Ubiquiti UniFi', 'MikroTik'])
            criticality = 'critical' if device_type in ['router', 'firewall'] else 'high'
            owner = 'Network Team'
            department = 'IT'
            location = random.choice(['Data Center', 'Office Floor 1', 'Office Floor 2'])
            
        else:  # mobile
            asset_name = f"mobile-{random.randint(1, 20):02d}"
            hostname = None
            os_name = random.choice(['iOS 16', 'iOS 17', 'Android 13', 'Android 14'])
            criticality = 'medium'
            owner = random.choice(user_names).replace('.', ' ').title()
            department = random.choice(departments)
            location = 'Remote'
        
        # Status
        status = random.choices(
            ['active', 'inactive', 'maintenance'],
            weights=[0.85, 0.1, 0.05]
        )[0]
        
        # Last patch date (random в последние 90 дней)
        days_ago = random.randint(0, 90)
        last_patch = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')
        
        # OS version
        if 'Ubuntu' in os_name:
            os_version = os_name.split()[1]
        elif 'Windows' in os_name:
            os_version = '10.0.19045' if '10' in os_name else '10.0.22621'
        elif 'macOS' in os_name:
            os_version = '13.4'
        elif 'CentOS' in os_name or 'Red Hat' in os_name:
            os_version = '8.5'
        else:
            os_version = '1.0'
        
        asset = {
            'asset_name': asset_name,
            'asset_type': asset_type,
            'ip_address': ip_address,
            'mac_address': mac_address,
            'hostname': hostname,
            'criticality': criticality,
            'business_unit': department,
            'location': location,
            'os_name': os_name,
            'os_version': os_version,
            'last_patch_date': last_patch,
            'status': status,
            'owner': owner,
            'assigned_team': department if asset_type != 'mobile' else 'Mobile Device Management',
            'metadata': json.dumps({
                'asset_id': asset_id,
                'purchase_date': (datetime.now() - timedelta(days=random.randint(365, 1825))).strftime('%Y-%m-%d'),
                'warranty_expires': (datetime.now() + timedelta(days=random.randint(0, 730))).strftime('%Y-%m-%d')
            })
        }
        
        assets.append(asset)
        asset_id += 1
    
    return assets


def save_to_json(assets, filename='data/samples/assets.json'):
    """Сохраняет assets в JSON файл"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(assets, f, indent=2, ensure_ascii=False)
    print(f"Generated {len(assets)} assets")
    print(f"Saved to: {filename}")


def save_to_sql(assets, filename='data/samples/assets.sql'):
    """Сохраняет assets в SQL INSERT statements"""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("-- Generated Assets Data\n")
        f.write("-- Generated at: {}\n\n".format(datetime.now().isoformat()))
        
        for asset in assets:
            f.write("INSERT INTO assets (")
            f.write("asset_name, asset_type, ip_address, mac_address, hostname, ")
            f.write("criticality, business_unit, location, os_name, os_version, ")
            f.write("last_patch_date, status, owner, assigned_team, metadata")
            f.write(") VALUES (")
            
            values = [
                f"'{asset['asset_name']}'",
                f"'{asset['asset_type']}'",
                f"'{asset['ip_address']}'",
                f"'{asset['mac_address']}'",
                f"'{asset['hostname']}'" if asset['hostname'] else "NULL",
                f"'{asset['criticality']}'",
                f"'{asset['business_unit']}'",
                f"'{asset['location']}'",
                f"'{asset['os_name']}'",
                f"'{asset['os_version']}'",
                f"'{asset['last_patch_date']}'",
                f"'{asset['status']}'",
                f"'{asset['owner']}'",
                f"'{asset['assigned_team']}'",
                f"'{asset['metadata']}'"
            ]
            
            f.write(", ".join(values))
            f.write(");\n")
    
    print(f"Saved SQL to: {filename}")


def print_summary(assets):
    """Выводит статистику по сгенерированным assets"""
    print("\nAssets Summary:")
    print("-" * 50)
    
    # По типам
    types = {}
    for asset in assets:
        asset_type = asset['asset_type']
        types[asset_type] = types.get(asset_type, 0) + 1
    
    print("By Type:")
    for asset_type, count in sorted(types.items()):
        print(f"  {asset_type}: {count}")
    
    # По criticality
    criticality = {}
    for asset in assets:
        crit = asset['criticality']
        criticality[crit] = criticality.get(crit, 0) + 1
    
    print("\nBy Criticality:")
    for crit, count in sorted(criticality.items(), key=lambda x: ['critical', 'high', 'medium', 'low'].index(x[0])):
        print(f"  {crit}: {count}")
    
    # По OS
    os_types = {}
    for asset in assets:
        os_name = asset['os_name'].split()[0]  # Берем только название ОС
        os_types[os_name] = os_types.get(os_name, 0) + 1
    
    print("\nBy OS:")
    for os_name, count in sorted(os_types.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  {os_name}: {count}")


if __name__ == "__main__":
    # Генерируем 50 assets
    assets = generate_assets(count=50)
    
    # Сохраняем
    save_to_json(assets)
    save_to_sql(assets)
    
    # Выводим статистику
    print_summary(assets)
    
    print("\nDone!")
