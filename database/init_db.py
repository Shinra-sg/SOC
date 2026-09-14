#!/usr/bin/env python3
"""
AI-SOC Database Initialization Script
Инициализирует базу данных (PostgreSQL или SQLite)
"""

import os
import sys
import sqlite3
from pathlib import Path
from typing import Optional

try:
    import psycopg2
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False
    print("⚠️  Warning: psycopg2 not installed. PostgreSQL support disabled.")


def init_sqlite(db_path: str = "database/ai_soc.db") -> bool:
    """
    Инициализирует SQLite базу данных
    
    Args:
        db_path: Путь к файлу базы данных
        
    Returns:
        True если успешно, False если ошибка
    """
    try:
        print(f"📦 Initializing SQLite database: {db_path}")
        
        # Создаем директорию если не существует
        db_dir = Path(db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)
        
        # Путь к SQL схеме
        schema_path = Path(__file__).parent / "schema_sqlite.sql"
        
        if not schema_path.exists():
            print(f"❌ Schema file not found: {schema_path}")
            return False
        
        # Читаем схему
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        # Подключаемся и создаем схему
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Выполняем схему (разбиваем по ;)
        for statement in schema_sql.split(';'):
            statement = statement.strip()
            if statement:
                try:
                    cursor.execute(statement)
                except sqlite3.Error as e:
                    # Игнорируем ошибки "already exists"
                    if "already exists" not in str(e).lower():
                        print(f"⚠️  Warning: {e}")
        
        conn.commit()
        conn.close()
        
        print("✅ SQLite database initialized successfully!")
        print(f"   Location: {Path(db_path).absolute()}")
        
        # Проверяем созданные таблицы
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = cursor.fetchall()
        conn.close()
        
        print(f"   Tables created: {len(tables)}")
        for table in tables:
            print(f"      - {table[0]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error initializing SQLite database: {e}")
        return False


def init_postgresql(
    host: str = "localhost",
    port: int = 5432,
    database: str = "ai_soc",
    user: str = "postgres",
    password: Optional[str] = None
) -> bool:
    """
    Инициализирует PostgreSQL базу данных
    
    Args:
        host: Хост PostgreSQL
        port: Порт PostgreSQL
        database: Имя базы данных
        user: Пользователь
        password: Пароль
        
    Returns:
        True если успешно, False если ошибка
    """
    if not POSTGRES_AVAILABLE:
        print("❌ PostgreSQL support not available. Install psycopg2-binary:")
        print("   pip install psycopg2-binary")
        return False
    
    try:
        print(f"🐘 Initializing PostgreSQL database: {database}")
        
        # Путь к SQL схеме
        schema_path = Path(__file__).parent / "schema.sql"
        
        if not schema_path.exists():
            print(f"❌ Schema file not found: {schema_path}")
            return False
        
        # Читаем схему
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        # Подключаемся к PostgreSQL
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Выполняем схему
        cursor.execute(schema_sql)
        
        cursor.close()
        conn.close()
        
        print("✅ PostgreSQL database initialized successfully!")
        print(f"   Host: {host}:{port}")
        print(f"   Database: {database}")
        
        # Проверяем созданные таблицы
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password
        )
        cursor = conn.cursor()
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        tables = cursor.fetchall()
        cursor.close()
        conn.close()
        
        print(f"   Tables created: {len(tables)}")
        for table in tables:
            print(f"      - {table[0]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error initializing PostgreSQL database: {e}")
        return False


def main():
    """Main entry point"""
    print("\n" + "="*60)
    print("🔐 AI-SOC Database Initialization")
    print("="*60 + "\n")
    
    # Проверяем аргументы командной строки
    db_type = os.getenv('DB_TYPE', 'sqlite').lower()
    
    if len(sys.argv) > 1:
        db_type = sys.argv[1].lower()
    
    if db_type == 'sqlite':
        # Используем SQLite
        db_path = os.getenv('DB_PATH', 'database/ai_soc.db')
        success = init_sqlite(db_path)
        
    elif db_type == 'postgresql' or db_type == 'postgres':
        # Используем PostgreSQL
        host = os.getenv('DB_HOST', 'localhost')
        port = int(os.getenv('DB_PORT', '5432'))
        database = os.getenv('DB_NAME', 'ai_soc')
        user = os.getenv('DB_USER', 'postgres')
        password = os.getenv('DB_PASSWORD')
        
        if not password:
            print("⚠️  Warning: DB_PASSWORD not set in environment")
            password = input("Enter PostgreSQL password: ")
        
        success = init_postgresql(host, port, database, user, password)
        
    else:
        print(f"❌ Unknown database type: {db_type}")
        print("   Supported types: sqlite, postgresql")
        sys.exit(1)
    
    print("\n" + "="*60)
    if success:
        print("✅ Database initialization completed successfully!")
    else:
        print("❌ Database initialization failed!")
    print("="*60 + "\n")
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
