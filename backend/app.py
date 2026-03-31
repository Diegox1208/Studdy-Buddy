from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv
from database import StudyBuddyDB
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import functools

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Secret key for JWT
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')

# Configure CORS - allow all origins temporarily for debugging
CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

# Create uploads directory
UPLOAD_FOLDER = Path(__file__).parent / 'uploads'
UPLOAD_FOLDER.mkdir(exist_ok=True)

# Initialize database (use absolute path)
DB_PATH = Path(__file__).parent / 'studybuddy.db'
db = StudyBuddyDB(str(DB_PATH))

# Store file metadata in memory (for testing)
files_db = []

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Handle file upload"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Save file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    safe_filename = f"{timestamp}_{file.filename}"
    file_path = UPLOAD_FOLDER / safe_filename
    
    file.save(file_path)
    
    # Store metadata
    file_info = {
        'file_id': len(files_db) + 1,
        'filename': file.filename,
        'saved_as': safe_filename,
        'file_path': str(file_path),
        'size': os.path.getsize(file_path),
        'uploaded_at': datetime.now().isoformat(),
        'type': file.content_type
    }
    files_db.append(file_info)
    
    print(f"✅ File saved: {file_path}")
    print(f"📊 Total files: {len(files_db)}")
    
    return jsonify(file_info), 200

@app.route('/api/files', methods=['GET'])
def list_files():
    """List all uploaded files"""
    return jsonify(files_db), 200

@app.route('/api/files/<int:file_id>', methods=['DELETE'])
def delete_file(file_id):
    """Delete a file"""
    global files_db
    file_info = next((f for f in files_db if f['file_id'] == file_id), None)
    
    if not file_info:
        return jsonify({'error': 'File not found'}), 404
    
    # Delete physical file
    file_path = Path(file_info['file_path'])
    if file_path.exists():
        file_path.unlink()
    
    # Remove from database
    files_db = [f for f in files_db if f['file_id'] != file_id]
    
    print(f"🗑️ File deleted: {file_info['filename']}")
    
    return jsonify({'message': 'File deleted'}), 200

@app.route('/uploads/<path:filename>')
def serve_file(filename):
    """Serve uploaded files"""
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/health')
def health():
    """Health check"""
    return jsonify({
        'status': 'running',
        'upload_folder': str(UPLOAD_FOLDER),
        'total_files': len(files_db)
    })

# ============================================
# AUTHENTICATION ENDPOINTS
# ============================================

@app.route('/api/signup', methods=['POST'])
def signup():
    """Register a new user (student or professor)"""
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['email', 'password', 'nombre', 'apellido', 'role']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing field: {field}'}), 400
        
        email = data['email'].lower().strip()
        password = data['password']
        nombre = data['nombre']
        apellido = data['apellido']
        role = data['role']  # 'student' or 'professor'
        
        # Validate role
        if role not in ['student', 'professor']:
            return jsonify({'error': 'Invalid role. Must be "student" or "professor"'}), 400
        
        # Hash password
        password_hash = generate_password_hash(password)
        
        db.connect()
        
        # Check if email already exists
        if role == 'student':
            db.cursor.execute("SELECT id FROM estudiantes WHERE email = ?", (email,))
        else:
            db.cursor.execute("SELECT id FROM profesores WHERE email = ?", (email,))
        
        if db.cursor.fetchone():
            db.close()
            return jsonify({'error': 'Email already registered'}), 409
        
        # Create user
        if role == 'student':
            edad = data.get('edad', 15)
            nivel_educativo = data.get('nivel_educativo', 'Secundaria')
            
            db.cursor.execute("""
                INSERT INTO estudiantes (nombre, apellido, email, password_hash, edad, nivel_educativo)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (nombre, apellido, email, password_hash, edad, nivel_educativo))
        else:
            especialidad = data.get('especialidad', 'General')
            
            db.cursor.execute("""
                INSERT INTO profesores (nombre, apellido, email, password_hash, especialidad)
                VALUES (?, ?, ?, ?, ?)
            """, (nombre, apellido, email, password_hash, especialidad))
        
        db.conn.commit()
        user_id = db.cursor.lastrowid
        db.close()
        
        # Generate JWT token
        token = jwt.encode({
            'user_id': user_id,
            'email': email,
            'role': role,
            'exp': datetime.utcnow() + timedelta(days=7)
        }, app.config['SECRET_KEY'], algorithm='HS256')
        
        return jsonify({
            'message': 'User created successfully',
            'token': token,
            'user': {
                'id': user_id,
                'email': email,
                'nombre': nombre,
                'apellido': apellido,
                'role': role
            }
        }), 201
        
    except Exception as e:
        print(f"❌ Signup error: {str(e)}")
        return jsonify({'error': 'Signup failed', 'details': str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    """Authenticate user and return JWT token"""
    try:
        data = request.json
        
        # Validate required fields
        if 'email' not in data or 'password' not in data:
            return jsonify({'error': 'Email and password required'}), 400
        
        email = data['email'].lower().strip()
        password = data['password']
        
        db.connect()
        
        # Try to find user in students table
        db.cursor.execute("""
            SELECT id, nombre, apellido, email, password_hash 
            FROM estudiantes WHERE email = ? AND activo = 1
        """, (email,))
        user = db.cursor.fetchone()
        role = 'student'
        
        # If not found, try professors table
        if not user:
            db.cursor.execute("""
                SELECT id, nombre, apellido, email, password_hash 
                FROM profesores WHERE email = ? AND activo = 1
            """, (email,))
            user = db.cursor.fetchone()
            role = 'professor'
        
        db.close()
        
        if not user:
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Verify password
        user_dict = dict(user)
        if not check_password_hash(user_dict['password_hash'], password):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Generate JWT token
        token = jwt.encode({
            'user_id': user_dict['id'],
            'email': user_dict['email'],
            'role': role,
            'exp': datetime.utcnow() + timedelta(days=7)
        }, app.config['SECRET_KEY'], algorithm='HS256')
        
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': {
                'id': user_dict['id'],
                'email': user_dict['email'],
                'nombre': user_dict['nombre'],
                'apellido': user_dict['apellido'],
                'role': role
            }
        }), 200
        
    except Exception as e:
        print(f"❌ Login error: {str(e)}")
        return jsonify({'error': 'Login failed', 'details': str(e)}), 500

@app.route('/api/user', methods=['GET'])
def get_current_user():
    """Get current user info from JWT token"""
    try:
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'No token provided'}), 401
        
        token = auth_header.split(' ')[1]
        
        # Decode token
        try:
            payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        
        user_id = payload['user_id']
        role = payload['role']
        
        db.connect()
        
        # Get user info
        if role == 'student':
            db.cursor.execute("""
                SELECT id, nombre, apellido, email, edad, nivel_educativo, foto_perfil
                FROM estudiantes WHERE id = ? AND activo = 1
            """, (user_id,))
        else:
            db.cursor.execute("""
                SELECT id, nombre, apellido, email, especialidad, foto_perfil
                FROM profesores WHERE id = ? AND activo = 1
            """, (user_id,))
        
        user = db.cursor.fetchone()
        db.close()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        user_dict = dict(user)
        user_dict['role'] = role
        
        return jsonify({'user': user_dict}), 200
        
    except Exception as e:
        print(f"❌ Get user error: {str(e)}")
        return jsonify({'error': 'Failed to get user info', 'details': str(e)}), 500

@app.route('/api/bookings', methods=['POST'])
def create_booking():
    """Create a new class booking request"""
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['estudiante_id', 'materia', 'fecha', 'hora_inicio', 'hora_fin']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing field: {field}'}), 400
        
        # For now, assign to first available professor (you can add matching logic later)
        # Get the first active professor
        db.connect()
        db.cursor.execute("SELECT id FROM profesores WHERE activo = 1 LIMIT 1")
        profesor = db.cursor.fetchone()
        
        if not profesor:
            return jsonify({'error': 'No professors available'}), 404
        
        profesor_id = profesor[0]
        
        # Get materia_id from materia name
        materia_name_map = {
            'matematicas': 'Matemáticas',
            'fisica': 'Física',
            'quimica': 'Química',
            'biologia': 'Biología',
            'historia': 'Historia',
            'lengua': 'Lengua y Literatura',
            'ingles': 'Inglés',
            'frances': 'Francés',
            'programacion': 'Programación'
        }
        
        materia_name = materia_name_map.get(data['materia'].lower(), data['materia'])
        
        # Find or create materia
        db.cursor.execute("SELECT id FROM materias WHERE nombre = ?", (materia_name,))
        materia = db.cursor.fetchone()
        
        if not materia:
            # Create new materia
            db.cursor.execute(
                "INSERT INTO materias (nombre) VALUES (?)",
                (materia_name,)
            )
            db.conn.commit()
            materia_id = db.cursor.lastrowid
        else:
            materia_id = materia[0]
        
        # Create the class
        class_id = db.create_class(
            materia_id=materia_id,
            profesor_id=profesor_id,
            estudiante_id=data['estudiante_id'],
            fecha=data['fecha'],
            hora_inicio=data['hora_inicio'],
            hora_fin=data['hora_fin'],
            modalidad=data.get('modalidad', 'Virtual'),
            direccion=data.get('direccion'),
            link_virtual=data.get('link_virtual'),
            estado='programada'
        )
        
        db.close()
        
        return jsonify({
            'success': True,
            'class_id': class_id,
            'message': 'Clase programada exitosamente',
            'details': {
                'materia': materia_name,
                'fecha': data['fecha'],
                'hora_inicio': data['hora_inicio'],
                'hora_fin': data['hora_fin'],
                'profesor_id': profesor_id
            }
        }), 201
        
    except Exception as e:
        print(f"❌ Error creating booking: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/bookings', methods=['GET'])
def get_bookings():
    """Get all class bookings"""
    try:
        db.connect()
        
        # Get student_id from query params (optional)
        student_id = request.args.get('estudiante_id')
        profesor_id = request.args.get('profesor_id')
        
        query = """
            SELECT 
                c.id,
                c.fecha,
                c.hora_inicio,
                c.hora_fin,
                c.estado,
                c.modalidad,
                m.nombre as materia,
                e.nombre || ' ' || e.apellido as estudiante,
                p.nombre || ' ' || p.apellido as profesor
            FROM clases c
            JOIN materias m ON c.materia_id = m.id
            JOIN estudiantes e ON c.estudiante_id = e.id
            JOIN profesores p ON c.profesor_id = p.id
            WHERE 1=1
        """
        
        params = []
        if student_id:
            query += " AND c.estudiante_id = ?"
            params.append(student_id)
        
        if profesor_id:
            query += " AND c.profesor_id = ?"
            params.append(profesor_id)
        
        query += " ORDER BY c.fecha DESC, c.hora_inicio DESC"
        
        db.cursor.execute(query, params)
        bookings = [dict(row) for row in db.cursor.fetchall()]
        
        db.close()
        
        return jsonify(bookings), 200
        
    except Exception as e:
        print(f"❌ Error fetching bookings: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV', 'development') == 'development'
    
    print("🚀 Starting Study Buddy Backend...")
    print(f"📁 Upload folder: {UPLOAD_FOLDER}")
    print(f"🌐 Server: http://localhost:{port}")
    print(f"📤 Upload endpoint: http://localhost:{port}/api/upload")
    print(f"📅 Booking endpoint: http://localhost:{port}/api/bookings")
    print(f"🔧 Debug mode: {debug}")
    print("\nPress Ctrl+C to stop\n")
    
    app.run(debug=debug, host='0.0.0.0', port=port)
