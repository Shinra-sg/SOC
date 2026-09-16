"""
Database Connection Management
Управление подключениями к базе данных с connection pooling
"""

import os
from contextlib import contextmanager
from typing import Generator, Optional
from sqlalchemy import create_engine, event, Engine
from sqlalchemy.orm import sessionmaker, Session, DeclarativeBase
from sqlalchemy.pool import StaticPool, QueuePool


class Base(DeclarativeBase):
    """Base class для всех ORM моделей"""
    pass


class DatabaseConnection:
    """
    Singleton класс для управления подключениями к БД
    
    Поддерживает:
    - PostgreSQL (production)
    - SQLite (development/testing)
    - Connection pooling
    - Automatic session management
    """
    
    _instance: Optional['DatabaseConnection'] = None
    _engine: Optional[Engine] = None
    _session_factory: Optional[sessionmaker] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Инициализация (вызывается только один раз)"""
        if self._engine is None:
            self._initialize()
    
    def _initialize(self):
        """Инициализирует connection pool"""
        db_type = os.getenv('DB_TYPE', 'sqlite').lower()
        
        if db_type == 'postgresql' or db_type == 'postgres':
            self._init_postgresql()
        else:
            self._init_sqlite()
        
        # Create session factory
        self._session_factory = sessionmaker(
            bind=self._engine,
            autocommit=False,
            autoflush=False,
            expire_on_commit=False
        )
    
    def _init_postgresql(self):
        """Инициализация PostgreSQL connection"""
        host = os.getenv('DB_HOST', 'localhost')
        port = os.getenv('DB_PORT', '5432')
        database = os.getenv('DB_NAME', 'ai_soc')
        user = os.getenv('DB_USER', 'postgres')
        password = os.getenv('DB_PASSWORD', '')
        
        database_url = f"postgresql://{user}:{password}@{host}:{port}/{database}"
        
        self._engine = create_engine(
            database_url,
            poolclass=QueuePool,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,  # Check connection health
            pool_recycle=3600,   # Recycle connections after 1 hour
            echo=os.getenv('SQL_ECHO', 'false').lower() == 'true'
        )
        
        print(f"✓ PostgreSQL connection initialized: {host}:{port}/{database}")
    
    def _init_sqlite(self):
        """Инициализация SQLite connection"""
        db_path = os.getenv('DB_PATH', 'database/ai_soc.db')
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        database_url = f"sqlite:///{db_path}"
        
        self._engine = create_engine(
            database_url,
            poolclass=StaticPool,
            connect_args={'check_same_thread': False},
            echo=os.getenv('SQL_ECHO', 'false').lower() == 'true'
        )
        
        # Enable foreign keys for SQLite
        @event.listens_for(self._engine, "connect")
        def set_sqlite_pragma(dbapi_conn, connection_record):
            cursor = dbapi_conn.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()
        
        print(f"✓ SQLite connection initialized: {db_path}")
    
    @property
    def engine(self) -> Engine:
        """Возвращает SQLAlchemy engine"""
        if self._engine is None:
            self._initialize()
        return self._engine
    
    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """
        Context manager для работы с сессиями
        
        Usage:
            with db.get_session() as session:
                user = session.query(User).first()
        """
        session = self._session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    def create_session(self) -> Session:
        """
        Создает новую сессию (нужно закрыть вручную)
        
        Usage:
            session = db.create_session()
            try:
                user = session.query(User).first()
                session.commit()
            finally:
                session.close()
        """
        return self._session_factory()
    
    def create_all_tables(self):
        """Создает все таблицы в БД"""
        Base.metadata.create_all(self._engine)
        print("✓ All tables created")
    
    def drop_all_tables(self):
        """Удаляет все таблицы из БД"""
        Base.metadata.drop_all(self._engine)
        print("✓ All tables dropped")
    
    def dispose(self):
        """Закрывает все connections в pool"""
        if self._engine:
            self._engine.dispose()
            print("✓ Connection pool disposed")


# Global instance
db = DatabaseConnection()


def get_db_session() -> Session:
    """
    Dependency injection для FastAPI/Flask
    
    Usage:
        @app.get("/users")
        def get_users(session: Session = Depends(get_db_session)):
            return session.query(User).all()
    """
    return db.create_session()


@contextmanager
def session_scope() -> Generator[Session, None, None]:
    """
    Context manager для транзакций
    
    Usage:
        with session_scope() as session:
            user = User(name="John")
            session.add(user)
    """
    with db.get_session() as session:
        yield session
