"""
Migrate existing database to add password fields
"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / 'studybuddy.db'

def migrate_database():
    """Add password_hash and ultimo_acceso columns to existing tables"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Add password_hash column to estudiantes if it doesn't exist
        cursor.execute("PRAGMA table_info(estudiantes)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'password_hash' not in columns:
            print("Adding password_hash to estudiantes table...")
            cursor.execute("ALTER TABLE estudiantes ADD COLUMN password_hash VARCHAR(255)")
            print("✅ Added password_hash to estudiantes")
        else:
            print("✓ password_hash already exists in estudiantes")
        
        if 'ultimo_acceso' not in columns:
            print("Adding ultimo_acceso to estudiantes table...")
            cursor.execute("ALTER TABLE estudiantes ADD COLUMN ultimo_acceso TIMESTAMP")
            print("✅ Added ultimo_acceso to estudiantes")
        else:
            print("✓ ultimo_acceso already exists in estudiantes")
        
        # Add password_hash column to profesores if it doesn't exist
        cursor.execute("PRAGMA table_info(profesores)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'password_hash' not in columns:
            print("Adding password_hash to profesores table...")
            cursor.execute("ALTER TABLE profesores ADD COLUMN password_hash VARCHAR(255)")
            print("✅ Added password_hash to profesores")
        else:
            print("✓ password_hash already exists in profesores")
        
        if 'ultimo_acceso' not in columns:
            print("Adding ultimo_acceso to profesores table...")
            cursor.execute("ALTER TABLE profesores ADD COLUMN ultimo_acceso TIMESTAMP")
            print("✅ Added ultimo_acceso to profesores")
        else:
            print("✓ ultimo_acceso already exists in profesores")
        
        conn.commit()
        print("\n✅ Database migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Migration error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    migrate_database()
