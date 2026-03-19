"""
Database connection utilities for Emotion Detection project
Supports both local PostgreSQL and Supabase (cloud) via DATABASE_URL
"""
import os
import psycopg2
from psycopg2 import pool
from contextlib import contextmanager

# ── Try loading .env for local development ──
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not needed in production (Streamlit Cloud uses secrets)

# ── Try loading Streamlit secrets into env vars ──
try:
    import streamlit as st
    if hasattr(st, 'secrets'):
        for key in ['DATABASE_URL', 'DB_HOST', 'DB_PORT', 'DB_NAME', 'DB_USER', 'DB_PASSWORD']:
            if key in st.secrets:
                os.environ[key] = str(st.secrets[key])
except Exception:
    pass


def _get_db_config():
    """
    Build DB config from environment.
    Priority: DATABASE_URL (Supabase) > individual DB_* vars (local)
    """
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        return {'dsn': database_url}
    
    return {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': os.getenv('DB_PORT', '5432'),
        'database': os.getenv('DB_NAME', 'emotion_detection_db'),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD')
    }


# Connection pool
connection_pool = None


def init_connection_pool(minconn=1, maxconn=5):
    """Initialize the connection pool"""
    global connection_pool
    try:
        config = _get_db_config()
        connection_pool = psycopg2.pool.SimpleConnectionPool(
            minconn, maxconn, **config
        )
        print("Database connection pool created successfully")
        return True
    except Exception as e:
        print(f"Error creating connection pool: {e}")
        return False


def close_connection_pool():
    """Close all connections in the pool"""
    global connection_pool
    if connection_pool:
        connection_pool.closeall()
        print("Connection pool closed")


@contextmanager
def get_db_connection():
    """
    Context manager for database connections.
    Uses pool if available, otherwise creates a direct connection.
    """
    conn = None
    try:
        if connection_pool:
            conn = connection_pool.getconn()
        else:
            config = _get_db_config()
            conn = psycopg2.connect(**config)

        yield conn
        conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Database error: {e}")
        raise
    finally:
        if conn and connection_pool:
            connection_pool.putconn(conn)
        elif conn:
            conn.close()


def test_connection():
    """Test database connection"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT version();")
            db_version = cursor.fetchone()
            cursor.close()
            print("Database connection successful!")
            print(f"   PostgreSQL version: {db_version[0]}")
            return True
    except Exception as e:
        print(f"Connection test failed: {e}")
        return False


def get_table_info():
    """Get information about tables in the database"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """)
            tables = cursor.fetchall()
            cursor.close()
            print(f"\nTables in database:")
            for table in tables:
                print(f"   - {table[0]}")
            return tables
    except Exception as e:
        print(f"Error getting table info: {e}")
        return None


if __name__ == "__main__":
    print("Testing database connection...")
    if test_connection():
        get_table_info()
