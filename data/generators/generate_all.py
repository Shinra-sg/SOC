#!/usr/bin/env python3
"""
Master Data Generator
Генерирует все тестовые данные для AI-SOC
"""

import sys
import subprocess
from pathlib import Path


def run_generator(script_name):
    """Запускает генератор"""
    print(f"\n{'='*70}")
    print(f"Running: {script_name}")
    print('='*70)
    
    result = subprocess.run(
        ['python3', f'data/generators/{script_name}'],
        capture_output=False,
        text=True
    )
    
    if result.returncode != 0:
        print(f"ERROR: {script_name} failed!")
        return False
    
    return True


def main():
    """Main entry point"""
    print("\n" + "="*70)
    print("AI-SOC Test Data Generator")
    print("Generating all test data...")
    print("="*70)
    
    generators = [
        'generate_assets.py',
        'generate_ioc.py',
        'generate_cve.py',
        'generate_events.py'
    ]
    
    success_count = 0
    
    for generator in generators:
        if run_generator(generator):
            success_count += 1
        else:
            print(f"\nFailed at: {generator}")
            sys.exit(1)
    
    print("\n" + "="*70)
    print(f"SUCCESS: All {success_count}/{len(generators)} generators completed!")
    print("="*70)
    
    print("\nGenerated files:")
    print("  data/samples/assets.json + .sql")
    print("  data/samples/ioc.json + .sql")
    print("  data/samples/vulnerabilities.json + .sql")
    print("  data/samples/security_events.json + .sql")
    
    print("\nTo load into database:")
    print("  SQLite:     sqlite3 database/ai_soc.db < data/samples/*.sql")
    print("  PostgreSQL: psql -U postgres -d ai_soc < data/samples/*.sql")
    
    print("\nDone!")


if __name__ == "__main__":
    main()
