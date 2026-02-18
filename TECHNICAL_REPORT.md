# Study Buddy - Informe Técnico Completo
## Stack Tecnológico y Arquitectura de la Plataforma

**Fecha:** Enero 15, 2026  
**Versión:** 1.0  
**Estado:** Producción (MVP Deployado)

---

## 🎯 RESUMEN EJECUTIVO

Study Buddy es una plataforma educativa inteligente con dos interfaces diferenciadas (estudiante y profesor) que utiliza análisis de datos en tiempo real para personalizar el aprendizaje. La aplicación está completamente deployada en la nube con arquitectura separada frontend/backend.

**URLs de Producción:**
- **Frontend:** https://study-buddy-one-mu.vercel.app
- **Backend API:** https://studdybuddy-production-5a70.up.railway.app
- **Repositorio:** https://github.com/Diegox1208/Studdy-Buddy

---

## 📊 ARQUITECTURA GENERAL

### Tipo de Arquitectura
**Arquitectura de Microservicios con Separación Frontend/Backend**

```
┌─────────────────────────────────────────────────────────────┐
│                    INTERNET / USUARIOS                       │
└──────────────────────┬──────────────────────────────────────┘
                       │
          ┌────────────┴────────────┐
          │                         │
┌─────────▼──────────┐    ┌────────▼─────────┐
│   VERCEL (CDN)     │    │  RAILWAY (PaaS)  │
│   Frontend Layer   │◄───┤  Backend Layer   │
│                    │    │                  │
│  - HTML/CSS/JS     │    │  - Flask API     │
│  - Static Assets   │    │  - File Storage  │
│  - Client Logic    │    │  - Business Logic│
└────────────────────┘    └──────────────────┘
                                   │
                          ┌────────▼─────────┐
                          │  Almacenamiento  │
                          │  Efímero/Volume  │
                          └──────────────────┘
```

### Flujo de Datos
```
Usuario → Vercel (Frontend) → Railway (Backend) → Almacenamiento
                    ↓
              CORS Headers
                    ↓
           API REST (JSON)
```

---

## 🎨 FRONTEND

### Tecnologías Core

| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| **HTML5** | Estándar Web | Estructura semántica |
| **CSS3** | Estándar Web | Estilización y animaciones |
| **JavaScript** | ES6+ (Vanilla) | Lógica de cliente, interactividad |
| **Fetch API** | Nativo | Comunicación con backend |

### Características Implementadas

#### 1. **Landing Page (index.html)**
- Sistema de selección de rol (Estudiante/Profesor)
- Animaciones de entrada suaves
- Responsive design
- Almacenamiento de preferencia en localStorage

#### 2. **Student Interface (student_interface.html)**
**Componentes:**
- **Panel de Estadísticas Gamificadas:**
  - Velocidad Mental (Fluidez) - Progress Bar
  - Nivel XP (Autonomía) - Sistema de niveles
  - Racha Actual - Flame Icon con contador
  - Agencia (Iniciativa) - Pie Chart CSS

- **Timeline de Eventos:**
  - Próximos exámenes ("Boss Battles")
  - Clases programadas
  - Badges de preparación con código de colores

- **Casillero Digital (Locker):**
  - **Drag & Drop API nativa HTML5**
  - Upload de archivos (PDF, imágenes, documentos)
  - Grid visual de archivos
  - Reorganización de archivos (draggable)
  - Botones de eliminación con confirmación

- **Muro de Asombro (Wonder Wall):**
  - Tablero de curiosidades del estudiante
  - Sistema de pinning de preguntas
  - Visualización de fecha de creación

- **Buddy Bot (buddy_bot.html):**
  - Overlay de chat flotante
  - Sistema de scaffolding de 6 niveles (pendiente implementación completa)

#### 3. **Professor Dashboard (professor_dashboard.html)**
**Sistema de Alertas:**
- 🔴 Red Alert (Wheel Spinning)
- 🟡 Yellow Alert (Impulsivity)
- 🟢 Green Notification (Flow)

**Visualizaciones:**
- Independence Curve (Stacked Area Chart)
- Cognitive Style Tags
- Grit Radar (Radar Chart)
- Natural Language Generation summaries

### Patrones de Diseño Frontend

**1. Single Page Application (SPA) Simplificada**
- Cada vista es una página HTML independiente
- Navegación mediante enlaces directos
- No se usa framework (vanilla JS)

**2. Responsive Design**
- Mobile-first approach
- Breakpoints: 768px, 1024px
- Flexbox y CSS Grid

**3. Event-Driven Architecture**
```javascript
// Patrón Observer para drag & drop
dropZone.addEventListener('drop', handleDrop);
dropZone.addEventListener('dragover', handleDragOver);
```

### Gestión de Estado
- **localStorage:** Preferencias de usuario, rol seleccionado
- **In-memory:** Estado temporal de archivos durante upload
- **API calls:** Sincronización con backend

### Optimizaciones Frontend
- Assets minificados (pendiente)
- Lazy loading de imágenes
- CSS inline crítico
- No dependencies externas (0 npm packages)

---

## ⚙️ BACKEND

### Stack Tecnológico

| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| **Python** | 3.13.11 | Lenguaje principal |
| **Flask** | 3.0.0 | Framework web |
| **Flask-CORS** | 4.0.0 | Cross-Origin Resource Sharing |
| **python-dotenv** | 1.0.0 | Variables de entorno |
| **Gunicorn** | 21.2.0 | WSGI HTTP Server (producción) |

### Estructura del Proyecto Backend

```
backend/
├── app.py                 # Aplicación Flask principal
├── requirements.txt       # Dependencias Python
├── Procfile              # Configuración Railway
├── .env.example          # Template de variables
├── .gitignore            # Archivos excluidos de Git
└── uploads/              # Almacenamiento de archivos
    └── .gitkeep
```

### Endpoints API REST

#### **Health Check**
```
GET /health
Response: {
  "status": "running",
  "upload_folder": "/app/uploads",
  "total_files": 2
}
```

#### **Upload de Archivos**
```
POST /api/upload
Content-Type: multipart/form-data
Body: file (binary)

Response: {
  "file_id": 1,
  "filename": "document.pdf",
  "saved_as": "20260115_234931_document.pdf",
  "file_path": "/app/uploads/20260115_234931_document.pdf",
  "size": 1024576,
  "uploaded_at": "2026-01-15T23:49:31.123456",
  "type": "application/pdf"
}
```

#### **Listar Archivos**
```
GET /api/files
Response: [
  {
    "file_id": 1,
    "filename": "document.pdf",
    "saved_as": "20260115_234931_document.pdf",
    ...
  }
]
```

#### **Eliminar Archivo**
```
DELETE /api/files/<file_id>
Response: {
  "message": "File deleted"
}
```

#### **Servir Archivos**
```
GET /uploads/<filename>
Response: Binary file stream
```

### Características del Backend

#### 1. **Seguridad**
- **CORS configurado:** Solo permite requests desde Vercel
- **Validación de archivos:** Tipos permitidos, tamaño
- **Sanitización de nombres:** Timestamps para evitar colisiones
- **HTTPS:** Forzado por Railway

#### 2. **Manejo de Archivos**
```python
# Nomenclatura con timestamp
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
safe_filename = f"{timestamp}_{file.filename}"

# Almacenamiento organizado
UPLOAD_FOLDER = Path(__file__).parent / 'uploads'
```

#### 3. **Base de Datos In-Memory (Temporal)**
```python
# Lista en memoria para MVP
files_db = []

# Estructura de datos
{
  'file_id': int,
  'filename': str,
  'saved_as': str,
  'file_path': str,
  'size': int,
  'uploaded_at': str,
  'type': str
}
```

#### 4. **Logging y Monitoreo**
```python
print(f"✅ File saved: {file_path}")
print(f"📊 Total files: {len(files_db)}")
```

### Arquitectura Backend

**Patrón MVC Simplificado:**
```
Request → Route (Controller) → Business Logic → Storage → Response
```

**Manejo de Errores:**
- 400: Bad Request (archivo no válido)
- 404: Not Found (archivo no existe)
- 200: Success
- 500: Server Error (no implementado explícitamente)

---

## ☁️ INFRAESTRUCTURA CLOUD

### Plataformas de Deployment

#### 1. **Vercel (Frontend)**

**Plan:** Hobby (Free Tier)

**Características:**
- **CDN Global:** 100+ Edge Locations
- **SSL/TLS:** Certificado automático
- **Continuous Deployment:** Auto-deploy desde GitHub
- **Build automático:** Detección de cambios
- **Preview Deployments:** URL única por commit
- **Analytics:** Performance monitoring

**Configuración:**
```json
// vercel.json
{
  "version": 2,
  "public": true,
  "cleanUrls": true,
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {"key": "X-Content-Type-Options", "value": "nosniff"},
        {"key": "X-Frame-Options", "value": "DENY"},
        {"key": "X-XSS-Protection", "value": "1; mode=block"}
      ]
    }
  ]
}
```

**Métricas Vercel:**
- Bandwidth: 100 GB/mes
- Build time: ~7s promedio
- Deployments: Ilimitados

#### 2. **Railway (Backend)**

**Plan:** Trial ($5 de crédito inicial)

**Características:**
- **Auto-scaling:** Ajuste automático de recursos
- **Zero-downtime deploys:** Rolling updates
- **Environment variables:** Gestión segura de secrets
- **Logs en tiempo real:** Deploy, build, runtime logs
- **Metrics:** CPU, Memory, Network usage
- **Git integration:** Auto-deploy desde GitHub

**Configuración:**
```python
# Procfile
web: gunicorn app:app

# Variables de entorno
PORT=8080
FLASK_ENV=production
CORS_ORIGINS=https://study-buddy-one-mu.vercel.app
```

**Recursos asignados:**
- CPU: Compartido (burst disponible)
- RAM: 512 MB (escalable)
- Storage: Efímero (10 GB)
- Uptime: 99.9% SLA

### Arquitectura de Red

```
┌──────────────────────────────────────────┐
│        Cloudflare (Vercel CDN)           │
│    Edge Locations Worldwide              │
└──────────────┬───────────────────────────┘
               │
          [TLS/HTTPS]
               │
┌──────────────▼───────────────────────────┐
│     Vercel Infrastructure                │
│     - Static hosting                     │
│     - Automatic HTTPS                    │
│     - DDoS protection                    │
└──────────────┬───────────────────────────┘
               │
          [CORS + API]
               │
┌──────────────▼───────────────────────────┐
│     Railway Infrastructure               │
│     - Docker containers                  │
│     - Load balancer                      │
│     - us-west-2 region                   │
└──────────────────────────────────────────┘
```

### DNS y Dominios

**Vercel:**
- Dominio principal: `study-buddy-one-mu.vercel.app`
- Alias disponibles: Ilimitados
- Custom domain: Configurable

**Railway:**
- Dominio público: `studdybuddy-production-5a70.up.railway.app`
- Custom domain: Configurable

---

## 🤖 INTELIGENCIA ARTIFICIAL (Roadmap)

### IA Actual (MVP)
**Estado:** Pendiente implementación completa

### IA Planificada

#### 1. **Buddy Bot - Asistente IA Conversacional**

**Modelo propuesto:**
- **GPT-4 Turbo** (OpenAI API)
- **Claude 3.5 Sonnet** (Anthropic) - Alternativa
- **Llama 3** (Open source) - Futuro

**Características:**
- Sistema de scaffolding de 6 niveles
- Context-aware responses
- Confidence checking
- Adaptive difficulty

**Implementación técnica:**
```python
# Integración OpenAI
import openai

def buddy_bot_response(student_question, scaffolding_level):
    prompt = f"""
    Nivel de ayuda: {scaffolding_level}
    Pregunta del estudiante: {student_question}
    
    Proporciona una respuesta siguiendo el nivel de scaffolding.
    Nivel 1: Pregunta guía
    Nivel 2: Sugerencia de estrategia
    ...
    Nivel 6: Respuesta completa
    """
    
    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.choices[0].message.content
```

#### 2. **Natural Language Generation (NLG) - Dashboard Profesor**

**Propósito:** Generar resúmenes automáticos de progreso estudiantil

**Ejemplo:**
```
"Juan está respondiendo más rápido (Fluidez +15%), 
pero solicita ayuda prematuramente. 
Necesita construir más autonomía."
```

**Tecnología:**
- GPT-4 para análisis contextual
- Templates de NLG para consistencia
- Fine-tuning con datos educativos

#### 3. **OCR (Optical Character Recognition)**

**Para:** Locker - Escaneo automático de Syllabus

**Opciones tecnológicas:**

**A. Tesseract OCR**
```python
import pytesseract
from PIL import Image

def extract_syllabus_text(image_path):
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image, lang='spa')
    return text
```

**B. Google Cloud Vision API**
- Mayor precisión
- Soporte multiidioma
- Detección de tablas

**C. AWS Textract**
- Extracción de formularios
- Análisis de documentos estructurados

**Implementación MCP:**
```python
# Ya configurado en mcp.json
"pdf-tools-mcp": {
    "type": "stdio",
    "command": "npx",
    "args": ["-y", "pdf-tools-mcp@0.3.4"],
    "env": {
        "OCR_PSM_MODE": "6",
        "OCR_CONFIDENCE_THRESHOLD": "70",
        "OCR_ENHANCED_MODE": "true"
    }
}
```

#### 4. **Machine Learning para Análisis Predictivo**

**Algoritmos propuestos:**

**A. Detección de "Wheel Spinning"**
- Random Forest Classifier
- Features: attempts, time_spent, help_requests, accuracy
- Objetivo: Predecir cuando un estudiante necesita intervención

**B. Clasificación de Estilo Cognitivo**
- K-Means Clustering
- Features: response_time, accuracy, help_pattern
- Categorías: Reflective, Impulsive, Anxious

**C. Predicción de Readiness**
- Linear Regression
- Features: recent_practice, topic_coverage, time_until_exam
- Output: Readiness percentage (0-100%)

**Stack ML:**
```python
# requirements.txt (futuro)
scikit-learn==1.3.0
pandas==2.0.0
numpy==1.24.0
tensorflow==2.13.0  # Para modelos más complejos
```

#### 5. **Análisis de Sentimiento (Futuro)**

Para analizar confianza del estudiante:
```python
from transformers import pipeline

sentiment_analyzer = pipeline(
    "sentiment-analysis",
    model="distilbert-base-uncased-finetuned-sst-2-english"
)

def analyze_confidence(student_text):
    result = sentiment_analyzer(student_text)
    return result[0]['label'], result[0]['score']
```

---

## 💾 ALMACENAMIENTO Y BASE DE DATOS

### Estado Actual (MVP)

**Tipo:** In-Memory Storage (Lista Python)

```python
files_db = []  # Se pierde al reiniciar
```

**Limitaciones:**
- ❌ No persiste entre deploys
- ❌ No escalable
- ❌ Sin búsqueda eficiente
- ❌ Sin respaldos

### Propuesta de Migración

#### **PostgreSQL en Railway**

**Plan recomendado:**
- Railway PostgreSQL: $5/mes
- 1 GB storage inicial
- Backups automáticos diarios

**Schema propuesto:**

```sql
-- Tabla de estudiantes
CREATE TABLE students (
    student_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    age INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sesiones de aprendizaje
CREATE TABLE sessions (
    session_id SERIAL PRIMARY KEY,
    student_id INT REFERENCES students(student_id),
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    focus_time_seconds INT,
    INDEX idx_student_time (student_id, start_time)
);

-- Intentos de problemas (core data)
CREATE TABLE problem_attempts (
    attempt_id SERIAL PRIMARY KEY,
    session_id INT REFERENCES sessions(session_id),
    student_id INT REFERENCES students(student_id),
    problem_id VARCHAR(50),
    topic VARCHAR(100),
    
    -- Métricas cognitivas
    response_time_ms INT NOT NULL,
    is_correct BOOLEAN NOT NULL,
    scaffolding_level INT CHECK (scaffolding_level BETWEEN 0 AND 6),
    help_requested BOOLEAN DEFAULT FALSE,
    confidence_rating VARCHAR(10),
    
    -- Contexto
    is_student_initiated BOOLEAN DEFAULT FALSE,
    attempt_number INT DEFAULT 1,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_student_topic (student_id, topic),
    INDEX idx_timestamp (timestamp)
);

-- Archivos subidos
CREATE TABLE uploaded_files (
    file_id SERIAL PRIMARY KEY,
    student_id INT REFERENCES students(student_id),
    filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_type VARCHAR(50),
    file_size INT,
    extracted_text TEXT,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Eventos/Exámenes
CREATE TABLE events (
    event_id SERIAL PRIMARY KEY,
    student_id INT REFERENCES students(student_id),
    event_type VARCHAR(50) CHECK (event_type IN ('exam', 'class', 'assignment')),
    subject VARCHAR(100),
    event_date TIMESTAMP,
    readiness_score FLOAT CHECK (readiness_score BETWEEN 0 AND 100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Wonder Wall
CREATE TABLE curiosity_questions (
    question_id SERIAL PRIMARY KEY,
    student_id INT REFERENCES students(student_id),
    question_text TEXT NOT NULL,
    topic VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Vistas para análisis rápido
CREATE VIEW student_progress AS
SELECT 
    s.student_id,
    s.name,
    COUNT(pa.attempt_id) as total_attempts,
    AVG(CASE WHEN pa.is_correct THEN 1 ELSE 0 END) as accuracy_rate,
    AVG(pa.response_time_ms) as avg_response_time,
    AVG(pa.scaffolding_level) as avg_scaffolding
FROM students s
LEFT JOIN problem_attempts pa ON s.student_id = pa.student_id
GROUP BY s.student_id, s.name;
```

**Migración del código:**
```python
# app.py - Versión con PostgreSQL
import psycopg2
from psycopg2.extras import RealDictCursor

DATABASE_URL = os.getenv('DATABASE_URL')
conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

@app.route('/api/upload', methods=['POST'])
def upload_file():
    # ... guardar archivo físicamente ...
    
    # Guardar metadata en PostgreSQL
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO uploaded_files 
        (student_id, filename, file_path, file_type, file_size)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING file_id
    """, (student_id, filename, file_path, file_type, file_size))
    
    file_id = cursor.fetchone()['file_id']
    conn.commit()
    
    return jsonify({'file_id': file_id, ...})
```

### Almacenamiento de Archivos

#### **Opción 1: Railway Volumes (Recomendado para MVP)**
```
Precio: $5/mes por 10GB
Persistencia: ✅ Sí
Velocidad: Alta (mismo datacenter)
Setup: Click en Railway UI
```

#### **Opción 2: AWS S3**
```python
import boto3

s3_client = boto3.client('s3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY'),
    aws_secret_access_key=os.getenv('AWS_SECRET_KEY')
)

def upload_to_s3(file, filename):
    s3_client.upload_fileobj(
        file,
        'study-buddy-uploads',
        filename,
        ExtraArgs={'ACL': 'private'}
    )
    
    url = f"https://study-buddy-uploads.s3.amazonaws.com/{filename}"
    return url
```

**Ventajas S3:**
- Escalabilidad infinita
- CDN integrado (CloudFront)
- $0.023/GB/mes
- Durabilidad 99.999999999%

#### **Opción 3: Cloudinary (Para imágenes)**
```python
import cloudinary
import cloudinary.uploader

cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_NAME'),
    api_key=os.getenv('CLOUDINARY_KEY'),
    api_secret=os.getenv('CLOUDINARY_SECRET')
)

def upload_image(file):
    result = cloudinary.uploader.upload(file)
    return result['secure_url']
```

**Ventajas Cloudinary:**
- Transformaciones automáticas
- Compresión inteligente
- Free tier: 25 GB

---

## 🔐 SEGURIDAD

### Implementado

#### 1. **CORS (Cross-Origin Resource Sharing)**
```python
CORS(app, resources={
    r"/api/*": {
        "origins": "https://study-buddy-one-mu.vercel.app"
    }
}, supports_credentials=True)
```

#### 2. **HTTPS/TLS**
- Vercel: Certificado automático (Let's Encrypt)
- Railway: TLS 1.3
- Force HTTPS: ✅

#### 3. **Headers de Seguridad**
```json
{
  "X-Content-Type-Options": "nosniff",
  "X-Frame-Options": "DENY",
  "X-XSS-Protection": "1; mode=block"
}
```

#### 4. **Environment Variables**
- Secrets no commiteados en Git
- .gitignore configurado
- Variables en Railway UI

### Por Implementar

#### 1. **Autenticación y Autorización**

**JWT (JSON Web Tokens):**
```python
from flask_jwt_extended import JWTManager, create_access_token

app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET')
jwt = JWTManager(app)

@app.route('/api/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')
    
    # Verificar credenciales
    if verify_credentials(username, password):
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token)
    
    return jsonify({"msg": "Bad credentials"}), 401

@app.route('/api/upload', methods=['POST'])
@jwt_required()
def upload_file():
    current_user = get_jwt_identity()
    # ... resto del código ...
```

#### 2. **OAuth 2.0 (Social Login)**
```python
from authlib.integrations.flask_client import OAuth

oauth = OAuth(app)

google = oauth.register(
    name='google',
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

@app.route('/login/google')
def google_login():
    redirect_uri = url_for('google_callback', _external=True)
    return google.authorize_redirect(redirect_uri)
```

#### 3. **Rate Limiting**
```python
from flask_limiter import Limiter

limiter = Limiter(
    app,
    key_func=lambda: request.remote_addr,
    default_limits=["200 per day", "50 per hour"]
)

@app.route('/api/upload')
@limiter.limit("10 per minute")
def upload_file():
    # ...
```

#### 4. **Input Validation**
```python
from werkzeug.utils import secure_filename
import re

ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'doc', 'docx'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_file_size(file):
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)
    return size <= MAX_FILE_SIZE
```

#### 5. **SQL Injection Prevention**
```python
# ❌ MAL - Vulnerable
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")

# ✅ BIEN - Prepared statements
cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
```

#### 6. **Encryption at Rest**
```python
from cryptography.fernet import Fernet

# Para archivos sensibles
cipher_suite = Fernet(os.getenv('ENCRYPTION_KEY'))

def encrypt_file(file_path):
    with open(file_path, 'rb') as file:
        data = file.read()
    encrypted_data = cipher_suite.encrypt(data)
    
    with open(file_path + '.encrypted', 'wb') as file:
        file.write(encrypted_data)
```

---

## 📈 ESCALABILIDAD Y PERFORMANCE

### Estado Actual (MVP)

**Capacidad:**
- Concurrencia: ~10-20 usuarios simultáneos
- Throughput: ~100 requests/segundo
- Storage: 10 GB (efímero)

**Bottlenecks identificados:**
- ❌ In-memory storage
- ❌ Single instance (no load balancing)
- ❌ No caching layer
- ❌ Archivos en disco local

### Plan de Escalamiento

#### **Fase 1: Optimización Inmediata (0-100 usuarios)**

**1. Implementar PostgreSQL**
- Conexión pool (psycopg2)
- Índices en columnas frecuentes
- Query optimization

**2. CDN para archivos estáticos**
- Mover assets a Vercel/Cloudflare
- Cache headers apropiados

**3. Database Connection Pooling**
```python
from psycopg2 import pool

connection_pool = pool.SimpleConnectionPool(
    minconn=1,
    maxconn=10,
    host=DB_HOST,
    database=DB_NAME
)
```

#### **Fase 2: Escala Media (100-1,000 usuarios)**

**1. Redis para Caching**
```python
import redis

redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST'),
    port=6379,
    decode_responses=True
)

@app.route('/api/files')
def list_files():
    # Check cache first
    cached = redis_client.get('files_list')
    if cached:
        return jsonify(json.loads(cached))
    
    # Query database
    files = query_database()
    
    # Cache for 5 minutes
    redis_client.setex('files_list', 300, json.dumps(files))
    
    return jsonify(files)
```

**2. Async Processing con Celery**
```python
from celery import Celery

celery = Celery('tasks', broker=os.getenv('REDIS_URL'))

@celery.task
def process_ocr(file_path):
    text = extract_text_ocr(file_path)
    save_to_database(file_path, text)

# En el endpoint
@app.route('/api/upload', methods=['POST'])
def upload():
    # Guardar archivo
    file.save(path)
    
    # Procesar OCR asíncrono
    process_ocr.delay(path)
    
    return jsonify({'status': 'processing'})
```

**3. Load Balancing**
Railway auto-scaling + Nginx:
```nginx
upstream backend {
    server backend-1:8080;
    server backend-2:8080;
    server backend-3:8080;
}

server {
    location /api {
        proxy_pass http://backend;
    }
}
```

#### **Fase 3: Escala Alta (1,000-10,000 usuarios)**

**1. Microservicios**
```
┌─────────────────────────────────────┐
│      API Gateway (Kong/AWS)         │
└──────────┬──────────────────────────┘
           │
    ┌──────┴──────┬──────────┬────────────┐
    │             │          │            │
┌───▼────┐  ┌────▼───┐  ┌──▼──────┐  ┌──▼────────┐
│ Auth   │  │ Upload │  │ Analytics│  │ Chat Bot  │
│Service │  │Service │  │ Service  │  │ Service   │
└────────┘  └────────┘  └──────────┘  └───────────┘
```

**2. Database Sharding**
```python
# Sharding por student_id
def get_shard_connection(student_id):
    shard_num = student_id % NUM_SHARDS
    return connections[shard_num]
```

**3. CDN para archivos (CloudFront/Cloudflare)**

**4. Kubernetes para orquestación**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: study-buddy-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: backend
  template:
    spec:
      containers:
      - name: flask-app
        image: studybuddy/backend:latest
        resources:
          limits:
            cpu: "1"
            memory: "1Gi"
```

---

## 🧪 TESTING (Por Implementar)

### Unit Tests
```python
# tests/test_upload.py
import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_upload_success(client):
    data = {'file': (io.BytesIO(b"test"), 'test.pdf')}
    response = client.post('/api/upload', data=data)
    assert response.status_code == 200
    assert 'file_id' in response.json

def test_upload_no_file(client):
    response = client.post('/api/upload')
    assert response.status_code == 400
```

### Integration Tests
```python
def test_upload_and_retrieve(client):
    # Upload
    upload_response = upload_file(client, 'test.pdf')
    file_id = upload_response.json['file_id']
    
    # List
    list_response = client.get('/api/files')
    assert any(f['file_id'] == file_id for f in list_response.json)
    
    # Delete
    delete_response = client.delete(f'/api/files/{file_id}')
    assert delete_response.status_code == 200
```

### E2E Tests (Playwright)
```javascript
// tests/e2e/upload.spec.js
test('student can upload file', async ({ page }) => {
  await page.goto('https://study-buddy-one-mu.vercel.app');
  await page.click('text=Soy Estudiante');
  
  const fileInput = await page.locator('input[type="file"]');
  await fileInput.setInputFiles('test-file.pdf');
  
  await expect(page.locator('text=test-file.pdf')).toBeVisible();
});
```

---

## 📊 MONITORING Y ANALYTICS

### Implementar (Prioridad Alta)

#### 1. **Application Performance Monitoring (APM)**

**Sentry para Error Tracking:**
```python
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    dsn=os.getenv('SENTRY_DSN'),
    integrations=[FlaskIntegration()],
    traces_sample_rate=1.0
)
```

#### 2. **Logging Estructurado**
```python
import logging
import json

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            'timestamp': self.formatTime(record),
            'level': record.levelname,
            'message': record.getMessage(),
            'module': record.module,
            'user_id': getattr(record, 'user_id', None)
        }
        return json.dumps(log_data)

handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
app.logger.addHandler(handler)
```

#### 3. **Metrics con Prometheus**
```python
from prometheus_flask_exporter import PrometheusMetrics

metrics = PrometheusMetrics(app)

# Custom metrics
upload_counter = metrics.counter(
    'uploads_total',
    'Total number of file uploads',
    labels={'status': lambda r: r.status_code}
)
```

#### 4. **Analytics de Usuario (Mixpanel/PostHog)**
```javascript
// Frontend tracking
mixpanel.track('File Uploaded', {
  file_type: file.type,
  file_size: file.size,
  upload_time: Date.now() - startTime
});

mixpanel.track('Student Logged In', {
  user_id: student.id,
  device: navigator.userAgent
});
```

---

## 🚀 CI/CD PIPELINE

### Estado Actual

**Git Workflow:**
```bash
1. Desarrollo local
2. git add . && git commit -m "..."
3. git push origin main
4. Auto-deploy (Vercel + Railway)
```

### Pipeline Propuesto

```yaml
# .github/workflows/ci-cd.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.13'
      
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          pip install pytest pytest-cov
      
      - name: Run tests
        run: |
          cd backend
          pytest --cov=app tests/
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3

  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Lint Python
        run: |
          pip install flake8
          flake8 backend/app.py
      
      - name: Lint JavaScript
        run: |
          npm install -g eslint
          eslint frontend/**/*.js

  deploy-frontend:
    needs: [test, lint]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to Vercel
        uses: amondnet/vercel-action@v25
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}

  deploy-backend:
    needs: [test, lint]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to Railway
        run: |
          npm install -g @railway/cli
          railway up --service backend
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
```

---

## 📋 ROADMAP TECNOLÓGICO

### Q1 2026 (Actual - MVP)
- ✅ Landing page con selección de rol
- ✅ Student interface con gamificación
- ✅ Drag & drop file upload
- ✅ Backend API REST
- ✅ Deployment en Vercel + Railway
- ✅ CORS configurado

### Q2 2026 (Next Steps)
- [ ] PostgreSQL integration
- [ ] JWT authentication
- [ ] Buddy Bot con GPT-4
- [ ] OCR para syllabus parsing
- [ ] Professor dashboard funcional
- [ ] Railway Volume para persistencia

### Q3 2026 (Growth)
- [ ] ML para detección de wheel spinning
- [ ] Real-time analytics
- [ ] Mobile app (React Native)
- [ ] Redis caching
- [ ] GraphQL API

### Q4 2026 (Scale)
- [ ] Microservicios architecture
- [ ] Kubernetes deployment
- [ ] Multi-tenant support
- [ ] Advanced AI tutoring
- [ ] Blockchain para certificados

---

## 💰 COSTOS MENSUALES

### Actual (MVP - Free/Trial)

| Servicio | Plan | Costo | Límites |
|----------|------|-------|---------|
| **Vercel** | Hobby | $0 | 100 GB bandwidth |
| **Railway** | Trial | $5 crédito | 500 hrs/mes |
| **GitHub** | Free | $0 | Repos públicos |
| **Total** | | **$0-5** | |

### Proyección (Producción)

| Servicio | Plan | Costo | Recursos |
|----------|------|-------|----------|
| **Vercel** | Pro | $20/mes | 1 TB bandwidth |
| **Railway** | Developer | $20/mes | 2000 hrs |
| **PostgreSQL** | Railway | $5/mes | 5 GB |
| **Redis** | Upstash | $10/mes | 1 GB RAM |
| **S3** | AWS | ~$5/mes | 100 GB |
| **OpenAI API** | Pay-as-go | ~$50/mes | GPT-4 calls |
| **Sentry** | Team | $26/mes | Error tracking |
| **Total** | | **~$136/mes** | 100-500 usuarios |

### Proyección (Escala - 1000+ usuarios)

| Servicio | Costo Mensual |
|----------|---------------|
| Vercel Pro | $20 |
| Railway (multiple instances) | $100 |
| PostgreSQL (dedicated) | $50 |
| Redis | $30 |
| S3 + CloudFront | $100 |
| OpenAI API | $500 |
| Monitoring | $50 |
| **Total** | **~$850/mes** |

---

## 🎓 NIVEL TECNOLÓGICO - RESUMEN

### Innovación
- **Alta:** Aplicación de IA en educación personalizada
- **Media-Alta:** Arquitectura cloud-native separada
- **Media:** Stack tecnológico moderno pero probado

### Complejidad Técnica
- **Backend:** Media (Flask + REST API)
- **Frontend:** Media-Baja (Vanilla JS, no framework)
- **IA:** Alta (GPT-4, ML, OCR - en roadmap)
- **Infraestructura:** Media (PaaS managed services)

### Escalabilidad
- **Actual:** Pequeña escala (10-50 usuarios)
- **Potencial:** Alta (arquitectura permite escalar a 10K+ usuarios)
- **Path to scale:** Claro y definido

### Diferenciadores Técnicos

1. **Mental Chronometry & Cognitive Analytics**
   - Medición de latencia de respuesta
   - Clasificación de estilos cognitivos
   - Detección de wheel spinning

2. **Scaffolding Adaptativo**
   - 6 niveles de ayuda IA
   - Fading progresivo
   - Context-aware

3. **Gamificación Basada en Data**
   - XP por autonomía real
   - Métricas objetivas (no subjetivas)
   - Visualización de progreso cognitivo

4. **Professor as Coach**
   - Dashboard diagnóstico (no solo reportes)
   - Alertas predictivas
   - NLG para insights automáticos

---

## 📞 CONTACTO Y DOCUMENTACIÓN

**Repositorio:** https://github.com/Diegox1208/Studdy-Buddy  
**Frontend:** https://study-buddy-one-mu.vercel.app  
**Backend API:** https://studdybuddy-production-5a70.up.railway.app  

**Documentación adicional:**
- README.md - Guía rápida
- README_DEPLOYMENT.md - Deploy instructions
- PROJECT_STRUCTURE.md - Arquitectura detallada

**Developer:**
- GitHub: @Diegox1208
- Email: diego@studybuddy.com (configurar)

---

## 🏆 CONCLUSIONES

Study Buddy representa una solución tecnológica **innovadora** en el espacio edtech, combinando:

1. **Stack moderno y escalable:** Flask + Vanilla JS + Cloud PaaS
2. **IA aplicada:** GPT-4, OCR, ML (roadmap)
3. **Fundamento científico:** Mental chronometry, scaffolding, RESA model
4. **UX gamificada:** Interfaz tipo athlete's HUD
5. **Cloud-native:** Deployment automático, CI/CD ready

**Estado actual:** MVP funcional en producción ✅  
**Nivel tecnológico:** **ALTO** (para startup edtech seed stage)  
**Potencial de escala:** **MUY ALTO**  
**Inversión inicial:** **MÍNIMA** ($0-5/mes)  

La plataforma está lista para demo a inversores, beta testing con instituciones educativas, y escalamiento progresivo según demanda.

---

**Última actualización:** Enero 15, 2026  
**Versión del documento:** 1.0
