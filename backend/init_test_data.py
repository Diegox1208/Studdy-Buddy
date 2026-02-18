"""
Initialize test data for Study Buddy
Creates sample students and professors for testing
"""

from database import StudyBuddyDB

def init_test_data():
    db = StudyBuddyDB('studybuddy.db')
    
    print("🔧 Initializing database...")
    db.initialize_database('database_schema.sql')
    
    print("\n👥 Creating test students...")
    
    # Create test student
    student_id = db.create_student(
        nombre='Alex',
        apellido='Johnson',
        email='alex.johnson@email.com',
        edad=16,
        nivel_educativo='IB Diploma',
        fecha_nacimiento='2010-05-15'
    )
    print(f"✅ Student created: Alex Johnson (ID: {student_id})")
    
    print("\n👨‍🏫 Creating test professors...")
    
    # Create test professors
    prof1 = db.create_professor(
        nombre='María',
        apellido='García',
        email='maria.garcia@studybuddy.com',
        especialidad='Matemáticas y Física'
    )
    print(f"✅ Professor created: María García (ID: {prof1})")
    
    prof2 = db.create_professor(
        nombre='Carlos',
        apellido='López',
        email='carlos.lopez@studybuddy.com',
        especialidad='Ciencias y Química'
    )
    print(f"✅ Professor created: Carlos López (ID: {prof2})")
    
    prof3 = db.create_professor(
        nombre='Ana',
        apellido='Martínez',
        email='ana.martinez@studybuddy.com',
        especialidad='Lengua e Historia'
    )
    print(f"✅ Professor created: Ana Martínez (ID: {prof3})")
    
    print("\n📚 Creating test subjects...")
    
    # Create subjects
    subjects = [
        ('Matemáticas', 'Álgebra, Geometría, Cálculo'),
        ('Física', 'Mecánica, Termodinámica, Electromagnetismo'),
        ('Química', 'Química Orgánica e Inorgánica'),
        ('Biología', 'Biología Celular y Molecular'),
        ('Historia', 'Historia Universal'),
        ('Lengua y Literatura', 'Literatura y Gramática'),
        ('Inglés', 'Inglés como Segunda Lengua'),
        ('Francés', 'Francés Básico e Intermedio'),
        ('Programación', 'Python, JavaScript, HTML/CSS')
    ]
    
    db.connect()
    for nombre, descripcion in subjects:
        db.cursor.execute(
            "INSERT INTO materias (nombre, descripcion) VALUES (?, ?)",
            (nombre, descripcion)
        )
    db.conn.commit()
    db.close()
    
    print(f"✅ Created {len(subjects)} subjects")
    
    print("\n✅ Test data initialization complete!")
    print("\n📊 Summary:")
    print(f"  - Students: 1 (Alex Johnson)")
    print(f"  - Professors: 3")
    print(f"  - Subjects: {len(subjects)}")
    print("\n🚀 You can now test the booking system!")
    print("   Student ID to use in frontend: 1")

if __name__ == '__main__':
    init_test_data()
