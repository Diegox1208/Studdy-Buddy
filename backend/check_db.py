import sqlite3

conn = sqlite3.connect('studybuddy.db')
cursor = conn.cursor()

# Count total bookings
cursor.execute('SELECT COUNT(*) FROM clases')
total = cursor.fetchone()[0]
print(f'\n📅 Total bookings in database: {total}\n')

if total > 0:
    # Get detailed booking info
    cursor.execute('''
        SELECT 
            c.id,
            c.fecha,
            c.hora_inicio,
            c.hora_fin,
            m.nombre as materia,
            e.nombre || " " || e.apellido as estudiante,
            p.nombre || " " || p.apellido as profesor,
            c.modalidad,
            c.estado
        FROM clases c
        JOIN materias m ON c.materia_id = m.id
        JOIN estudiantes e ON c.estudiante_id = e.id
        JOIN profesores p ON c.profesor_id = p.id
        ORDER BY c.fecha DESC, c.hora_inicio DESC
    ''')
    
    bookings = cursor.fetchall()
    print('✅ BOOKINGS FOUND:\n')
    print('=' * 80)
    
    for b in bookings:
        print(f'ID: {b[0]}')
        print(f'📅 Fecha: {b[1]}')
        print(f'🕐 Hora: {b[2]} - {b[3]}')
        print(f'📚 Materia: {b[4]}')
        print(f'👤 Estudiante: {b[5]}')
        print(f'👨‍🏫 Profesor: {b[6]}')
        print(f'📍 Modalidad: {b[7]}')
        print(f'✓ Estado: {b[8]}')
        print('=' * 80)
else:
    print('❌ No bookings found in database')
    print('\nMake sure to:')
    print('1. Click "Tomar Clase" button')
    print('2. Fill the form')
    print('3. Click "¡Estoy Listo!"')
    print('4. Check browser console for errors (F12)')

conn.close()
