from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import os
from io import BytesIO
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv
from database import StudyBuddyDB
from werkzeug.security import generate_password_hash, check_password_hash
import jwt

try:
    from supabase import create_client
except ImportError:
    create_client = None

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

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_ROLE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
SUPABASE_STORAGE_BUCKET = os.getenv('SUPABASE_STORAGE_BUCKET', 'studybuddy-files')
supabase_client = None
if SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY:
    if create_client is None:
        print("⚠️ Supabase credentials are configured, but supabase is not installed")
    else:
        supabase_client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)


def storage_path_to_url(path):
    return f"supabase://{SUPABASE_STORAGE_BUCKET}/{path}"


def is_supabase_storage_path(path):
    return isinstance(path, str) and path.startswith('supabase://')


def extract_supabase_storage_path(path):
    prefix = f"supabase://{SUPABASE_STORAGE_BUCKET}/"
    return path[len(prefix):] if path.startswith(prefix) else path.replace('supabase://', '', 1).split('/', 1)[-1]


def save_uploaded_file(file, filename):
    if supabase_client:
        storage_path = f"student-files/{filename}"
        file_bytes = file.read()
        supabase_client.storage.from_(SUPABASE_STORAGE_BUCKET).upload(
            storage_path,
            file_bytes,
            file_options={
                'content-type': file.content_type or 'application/octet-stream',
                'upsert': 'true'
            }
        )
        return storage_path_to_url(storage_path)

    filepath = UPLOAD_FOLDER / filename
    file.save(filepath)
    return str(filepath)


def delete_stored_file(filepath):
    if is_supabase_storage_path(filepath) and supabase_client:
        storage_path = extract_supabase_storage_path(filepath)
        supabase_client.storage.from_(SUPABASE_STORAGE_BUCKET).remove([storage_path])
        return

    local_path = Path(filepath)
    if local_path.exists():
        local_path.unlink()


def send_stored_file(filepath, download_name):
    if is_supabase_storage_path(filepath) and supabase_client:
        storage_path = extract_supabase_storage_path(filepath)
        file_bytes = supabase_client.storage.from_(SUPABASE_STORAGE_BUCKET).download(storage_path)
        return send_file(BytesIO(file_bytes), as_attachment=True, download_name=download_name)

    local_path = Path(filepath)
    if not local_path.exists():
        return jsonify({'error': 'File not found on disk'}), 404
    return send_from_directory(local_path.parent, local_path.name, as_attachment=True, download_name=download_name)

# Initialize database (use absolute path)
DB_PATH = Path(__file__).parent / 'studybuddy.db'
db = StudyBuddyDB(str(DB_PATH))

def ensure_material_storage():
    try:
        db.connect()
        db.cursor.execute("""
            CREATE TABLE IF NOT EXISTS student_folders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                estudiante_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (estudiante_id) REFERENCES estudiantes(id) ON DELETE CASCADE,
                UNIQUE(estudiante_id, name)
            )
        """)

        db.cursor.execute("PRAGMA table_info(pizarra_paginas)")
        notebook_columns = {column['name'] for column in db.cursor.fetchall()}
        if 'folder_id' not in notebook_columns:
            db.cursor.execute("ALTER TABLE pizarra_paginas ADD COLUMN folder_id INTEGER REFERENCES student_folders(id) ON DELETE SET NULL")

        db.cursor.execute("PRAGMA table_info(student_files)")
        file_columns = {column['name'] for column in db.cursor.fetchall()}
        if 'folder_id' not in file_columns:
            db.cursor.execute("ALTER TABLE student_files ADD COLUMN folder_id INTEGER REFERENCES student_folders(id) ON DELETE SET NULL")

        db.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_pizarra_paginas_estudiante
            ON pizarra_paginas(estudiante_id)
        """)
        db.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_pizarra_paginas_estudiante_titulo
            ON pizarra_paginas(estudiante_id, titulo)
        """)
        db.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_pizarra_paginas_folder
            ON pizarra_paginas(estudiante_id, folder_id)
        """)
        db.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_student_files_folder
            ON student_files(estudiante_id, folder_id)
        """)
        db.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_student_folders_estudiante
            ON student_folders(estudiante_id, name)
        """)
        db.conn.commit()
    except Exception as e:
        print(f"⚠️ Could not ensure material storage: {e}")
    finally:
        db.close()

ensure_material_storage()

# Serve frontend
@app.route('/')
def index():
    """Serve the main index page"""
    frontend_path = Path(__file__).parent.parent / 'frontend'
    return send_from_directory(frontend_path, 'index.html')

@app.route('/<path:filename>')
def serve_frontend(filename):
    """Serve frontend files"""
    frontend_path = Path(__file__).parent.parent / 'frontend'
    return send_from_directory(frontend_path, filename)

@app.route('/health')
def health():
    """Health check"""
    return jsonify({
        'status': 'running',
        'upload_folder': str(UPLOAD_FOLDER)
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

@app.route('/api/students', methods=['GET'])
def get_all_students():
    """Get all registered students"""
    try:
        db.connect()
        
        db.cursor.execute("""
            SELECT id, nombre, apellido, email, edad, nivel_educativo, foto_perfil, fecha_registro
            FROM estudiantes 
            WHERE activo = 1
            ORDER BY nombre, apellido
        """)
        
        students = db.cursor.fetchall()
        db.close()
        
        students_list = [dict(student) for student in students]
        
        return jsonify({'students': students_list}), 200
        
    except Exception as e:
        print(f"❌ Get students error: {str(e)}")
        return jsonify({'error': 'Failed to get students', 'details': str(e)}), 500

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
        
        profesor_id = profesor['id']
        
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
            materia_id = materia['id']
        
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
                e.id as estudiante_id,
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

@app.route('/api/students/<int:student_id>/notebook/pages', methods=['GET', 'POST'])
def notebook_pages(student_id):
    """Get all notebook pages or create a new page for a student"""
    try:
        db.connect()
        
        if request.method == 'GET':
            # Get all pages for this student
            folder_id = request.args.get('folder_id')
            params = [student_id]
            folder_filter = ""
            if folder_id:
                folder_filter = " AND folder_id = ?"
                params.append(folder_id)

            db.cursor.execute(f"""
                SELECT id, estudiante_id, folder_id, titulo, pagina_data, fecha_creacion, fecha_modificacion
                FROM pizarra_paginas
                WHERE estudiante_id = ?{folder_filter}
                ORDER BY fecha_modificacion DESC
            """, params)
            pages = [dict(row) for row in db.cursor.fetchall()]
            db.close()
            return jsonify({'pages': pages}), 200
            
        elif request.method == 'POST':
            # Create new page
            data = request.json
            titulo = data.get('titulo', 'Sin título')
            pagina_data = data.get('pagina_data', '')
            folder_id = data.get('folder_id')

            db.cursor.execute("SELECT id FROM estudiantes WHERE id = ?", (student_id,))
            if not db.cursor.fetchone():
                db.close()
                return jsonify({'error': 'Student not found'}), 404

            if folder_id is not None:
                db.cursor.execute("SELECT id FROM student_folders WHERE id = ? AND estudiante_id = ?", (folder_id, student_id))
                if not db.cursor.fetchone():
                    db.close()
                    return jsonify({'error': 'Folder not found'}), 404

            db.cursor.execute("""
                SELECT id FROM pizarra_paginas
                WHERE estudiante_id = ? AND titulo = ? AND COALESCE(folder_id, 0) = COALESCE(?, 0)
                ORDER BY fecha_modificacion DESC, id DESC
                LIMIT 1
            """, (student_id, titulo, folder_id))
            existing_page = db.cursor.fetchone()

            if existing_page:
                page_id = existing_page['id']
                db.cursor.execute("""
                    UPDATE pizarra_paginas
                    SET pagina_data = ?, fecha_modificacion = CURRENT_TIMESTAMP
                    WHERE id = ? AND estudiante_id = ?
                """, (pagina_data, page_id, student_id))
                db.conn.commit()
                db.close()
                return jsonify({'message': 'Page updated', 'page_id': page_id, 'estudiante_id': student_id}), 200
            
            db.cursor.execute("""
                INSERT INTO pizarra_paginas (estudiante_id, titulo, pagina_data, folder_id)
                VALUES (?, ?, ?, ?)
            """, (student_id, titulo, pagina_data, folder_id))
            db.conn.commit()
            page_id = db.cursor.lastrowid
            db.close()
            
            return jsonify({'message': 'Page created', 'page_id': page_id, 'estudiante_id': student_id}), 201
            
    except Exception as e:
        print(f"❌ Error with notebook pages: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/students/<int:student_id>/folders', methods=['GET', 'POST'])
def student_folders(student_id):
    """Get or create folders for a student. Only professor UI creates folders."""
    try:
        db.connect()

        db.cursor.execute("SELECT id FROM estudiantes WHERE id = ?", (student_id,))
        if not db.cursor.fetchone():
            db.close()
            return jsonify({'error': 'Student not found'}), 404

        if request.method == 'GET':
            db.cursor.execute("""
                SELECT
                    folders.id,
                    folders.estudiante_id,
                    folders.name,
                    folders.created_at,
                    folders.updated_at,
                    COUNT(DISTINCT pages.id) AS page_count,
                    COUNT(DISTINCT files.id) AS file_count
                FROM student_folders AS folders
                LEFT JOIN pizarra_paginas AS pages
                    ON pages.folder_id = folders.id AND pages.estudiante_id = folders.estudiante_id
                LEFT JOIN student_files AS files
                    ON files.folder_id = folders.id AND files.estudiante_id = folders.estudiante_id
                WHERE folders.estudiante_id = ?
                GROUP BY folders.id
                ORDER BY folders.name COLLATE NOCASE ASC
            """, (student_id,))
            folders = [dict(row) for row in db.cursor.fetchall()]
            db.close()
            return jsonify({'folders': folders}), 200

        data = request.json or {}
        name = (data.get('name') or '').strip()
        if not name:
            db.close()
            return jsonify({'error': 'Folder name is required'}), 400

        try:
            db.cursor.execute("""
                INSERT INTO student_folders (estudiante_id, name)
                VALUES (?, ?)
            """, (student_id, name))
            db.conn.commit()
        except Exception as insert_error:
            db.close()
            if 'UNIQUE' in str(insert_error).upper():
                return jsonify({'error': 'Folder already exists'}), 409
            raise

        folder_id = db.cursor.lastrowid
        db.close()
        return jsonify({'message': 'Folder created', 'folder': {
            'id': folder_id,
            'estudiante_id': student_id,
            'name': name,
            'page_count': 0,
            'file_count': 0
        }}), 201

    except Exception as e:
        print(f"❌ Error with student folders: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/students/<int:student_id>/folders/<int:folder_id>', methods=['PUT', 'DELETE'])
def student_folder(student_id, folder_id):
    """Rename or delete a student folder."""
    try:
        db.connect()

        db.cursor.execute("SELECT id FROM student_folders WHERE id = ? AND estudiante_id = ?", (folder_id, student_id))
        if not db.cursor.fetchone():
            db.close()
            return jsonify({'error': 'Folder not found'}), 404

        if request.method == 'PUT':
            data = request.json or {}
            name = (data.get('name') or '').strip()
            if not name:
                db.close()
                return jsonify({'error': 'Folder name is required'}), 400

            try:
                db.cursor.execute("""
                    UPDATE student_folders
                    SET name = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ? AND estudiante_id = ?
                """, (name, folder_id, student_id))
                db.conn.commit()
            except Exception as update_error:
                db.close()
                if 'UNIQUE' in str(update_error).upper():
                    return jsonify({'error': 'Folder already exists'}), 409
                raise

            db.close()
            return jsonify({'message': 'Folder updated', 'folder_id': folder_id, 'name': name}), 200

        db.cursor.execute("UPDATE pizarra_paginas SET folder_id = NULL WHERE folder_id = ? AND estudiante_id = ?", (folder_id, student_id))
        db.cursor.execute("UPDATE student_files SET folder_id = NULL WHERE folder_id = ? AND estudiante_id = ?", (folder_id, student_id))
        db.cursor.execute("DELETE FROM student_folders WHERE id = ? AND estudiante_id = ?", (folder_id, student_id))
        db.conn.commit()
        db.close()
        return jsonify({'message': 'Folder deleted', 'folder_id': folder_id}), 200

    except Exception as e:
        print(f"❌ Error with student folder: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/students/<int:student_id>/notebook/pages/<int:page_id>', methods=['GET', 'PUT', 'DELETE'])
def notebook_page(student_id, page_id):
    """Get, update, or delete a specific notebook page"""
    try:
        db.connect()
        
        if request.method == 'GET':
            # Get specific page data
            db.cursor.execute("""
                SELECT id, estudiante_id, folder_id, titulo, pagina_data, fecha_creacion, fecha_modificacion
                FROM pizarra_paginas
                WHERE id = ? AND estudiante_id = ?
            """, (page_id, student_id))
            page = db.cursor.fetchone()
            db.close()
            
            if not page:
                return jsonify({'error': 'Page not found'}), 404
            
            return jsonify(dict(page)), 200
            
        elif request.method == 'PUT':
            # Update page
            data = request.json
            titulo = data.get('titulo')
            pagina_data = data.get('pagina_data')
            
            updates = []
            params = []
            
            if titulo is not None:
                updates.append('titulo = ?')
                params.append(titulo)
            
            if pagina_data is not None:
                updates.append('pagina_data = ?')
                params.append(pagina_data)
            
            if updates:
                updates.append('fecha_modificacion = CURRENT_TIMESTAMP')
                params.extend([page_id, student_id])
                
                query = f"""
                    UPDATE pizarra_paginas 
                    SET {', '.join(updates)}
                    WHERE id = ? AND estudiante_id = ?
                """
                db.cursor.execute(query, params)
                if db.cursor.rowcount == 0:
                    db.close()
                    return jsonify({'error': 'Page not found'}), 404
                db.conn.commit()
            
            db.close()
            return jsonify({'message': 'Page updated', 'page_id': page_id, 'estudiante_id': student_id}), 200
            
        elif request.method == 'DELETE':
            # Delete page
            db.cursor.execute("""
                DELETE FROM pizarra_paginas WHERE id = ? AND estudiante_id = ?
            """, (page_id, student_id))
            deleted_count = db.cursor.rowcount
            db.conn.commit()
            db.close()
            
            if deleted_count == 0:
                return jsonify({'error': 'Page not found'}), 404
            return jsonify({'message': 'Page deleted', 'page_id': page_id, 'estudiante_id': student_id}), 200
            
    except Exception as e:
        print(f"❌ Error with notebook page: {e}")
        return jsonify({'error': str(e)}), 500

# File Management Endpoints
@app.route('/api/students/<int:student_id>/files', methods=['GET', 'POST'])
def student_files(student_id):
    """Get or upload files for a student"""
    try:
        if request.method == 'GET':
            # Get files by category
            category = request.args.get('category', 'casillero')
            folder_id = request.args.get('folder_id')
            params = [student_id, category]
            folder_filter = ""
            if folder_id:
                folder_filter = " AND folder_id = ?"
                params.append(folder_id)
            
            db.connect()
            db.cursor.execute(f"""
                SELECT id, estudiante_id, folder_id, filename, filepath, category, upload_date 
                FROM student_files 
                WHERE estudiante_id = ? AND category = ?
                {folder_filter}
                ORDER BY upload_date DESC
            """, params)
            
            files = [dict(row) for row in db.cursor.fetchall()]
            db.close()
            
            return jsonify({'files': files}), 200
            
        elif request.method == 'POST':
            # Upload new file
            if 'file' not in request.files:
                return jsonify({'error': 'No file provided'}), 400
            
            file = request.files['file']
            category = request.form.get('category', 'casillero')
            folder_id = request.form.get('folder_id')
            folder_id = int(folder_id) if folder_id else None
            
            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400
            
            db.connect()
            db.cursor.execute("SELECT id FROM estudiantes WHERE id = ?", (student_id,))
            if not db.cursor.fetchone():
                db.close()
                return jsonify({'error': 'Student not found'}), 404

            if folder_id is not None:
                db.cursor.execute("SELECT id FROM student_folders WHERE id = ? AND estudiante_id = ?", (folder_id, student_id))
                if not db.cursor.fetchone():
                    db.close()
                    return jsonify({'error': 'Folder not found'}), 404
            
            filename = f"{student_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
            filepath = save_uploaded_file(file, filename)
            
            # Store in database
            db.cursor.execute("""
                INSERT INTO student_files (estudiante_id, folder_id, filename, filepath, category)
                VALUES (?, ?, ?, ?, ?)
            """, (student_id, folder_id, file.filename, filepath, category))
            db.conn.commit()
            file_id = db.cursor.lastrowid
            db.close()
            
            return jsonify({
                'success': True,
                'file_id': file_id,
                'filename': file.filename
            }), 201
            
    except Exception as e:
        print(f"❌ Error with student files: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/student-files/<int:file_id>', methods=['DELETE'])
def delete_student_file(file_id):
    """Delete a student file"""
    try:
        db.connect()
        
        # Get file info
        db.cursor.execute("SELECT filepath FROM student_files WHERE id = ?", (file_id,))
        result = db.cursor.fetchone()
        
        if not result:
            db.close()
            return jsonify({'error': 'File not found'}), 404
        
        delete_stored_file(result['filepath'])
        
        # Delete from database
        db.cursor.execute("DELETE FROM student_files WHERE id = ?", (file_id,))
        db.conn.commit()
        db.close()
        
        return jsonify({'message': 'File deleted'}), 200
        
    except Exception as e:
        print(f"❌ Error deleting file: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/student-files/<int:file_id>/download', methods=['GET'])
def download_file(file_id):
    """Download a file"""
    try:
        db.connect()
        db.cursor.execute("SELECT filename, filepath FROM student_files WHERE id = ?", (file_id,))
        result = db.cursor.fetchone()
        db.close()
        
        if not result:
            return jsonify({'error': 'File not found'}), 404
        
        return send_stored_file(result['filepath'], result['filename'])
        
    except Exception as e:
        print(f"❌ Error downloading file: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV', 'development') == 'development'
    
    print("🚀 Starting Study Buddy Backend...")
    print(f"📁 Upload folder: {UPLOAD_FOLDER}")
    print(f"🌐 Server: http://localhost:{port}")
    print(f"📅 Booking endpoint: http://localhost:{port}/api/bookings")
    print(f"🔧 Debug mode: {debug}")
    print("\nPress Ctrl+C to stop\n")
    
    app.run(debug=debug, host='0.0.0.0', port=port)
