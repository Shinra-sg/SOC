#!/usr/bin/env python3
"""
Load Sample Data into Database
Загружает сгенерированные данные в базу данных
"""

import os
import sys
import sqlite3
from pathlib import Path


def load_sql_file(db_path, sql_file):
    """Загружает SQL файл в базу данных"""
    print(f"Loading: {sql_file}")
    
    if not Path(sql_file).exists():
        print(f"  ERROR: File not found: {sql_file}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # Split by INSERT statements and execute
        statements = [s.strip() for s in sql_content.split('INSERT INTO') if s.strip()]
        
        count = 0
        for statement in statements:
            if statement.startswith('--'):
                continue
            try:
                cursor.execute('INSERT INTO ' + statement)
                count += 1
            except sqlite3.Error as e:
                # Skip duplicates
                if 'UNIQUE constraint failed' not in str(e):
                    print(f"  Warning: {e}")
        
        conn.commit()
        conn.close()
        
        print(f"  ✓ Loaded {count} records")
        return True
        
    except Exception as e:
        print(f"  ERROR: {e}")
        return False


def main():
    """Main entry point"""
    print("\n" + "="*70)
    print("AI-SOC Sample Data Loader")
    print("="*70 + "\n")
    
    # Database path
    db_path = sys.argv[1] if len(sys.argv) > 1 else "database/ai_soc.db"
    
    if not Path(db_path).exists():
        print(f"ERROR: Database not found: {db_path}")
        print("Run: python3 database/init_db.py sqlite")
        sys.exit(1)
    
    print(f"Database: {db_path}\n")
    
    # SQL files to load (in order)
    sql_files = [
        'data/samples/assets.sql',
        'data/samples/ioc.sql',
        'data/samples/vulnerabilities.sql',
        'data/samples/security_events.sql'
    ]
    
    # Check if files exist
    missing = [f for f in sql_files if not Path(f).exists()]
    if missing:
        print("ERROR: Sample data files not found!")
        print("Missing files:")
        for f in missing:
            print(f"  - {f}")
        print("\nGenerate data first:")
        print("  python3 data/generators/generate_all.py")
        sys.exit(1)
    
    # Load each file
    success_count = 0
    for sql_file in sql_files:
        if load_sql_file(db_path, sql_file):
            success_count += 1
        print()
    
    print("="*70)
    if success_count == len(sql_files):
        print(f"SUCCESS: All {success_count}/{len(sql_files)} files loaded!")
    else:
        print(f"PARTIAL: {success_count}/{len(sql_files)} files loaded")
    print("="*70)
    
    # Show statistics
    print("\nDatabase Statistics:")
    print("-" * 70)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    tables = ['assets', 'indicators_of_compromise', 'vulnerabilities', 'security_events']
    
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"  {table:30s}: {count:5d} records")
    
    conn.close()
    
    print("\nDone!")


if __name__ == "__main__":
    main()
