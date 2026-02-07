-- Study Buddy Database Schema
-- Database for storing student information, classes, grades, reports, and metrics

-- ============================================
-- TABLA: Estudiantes (Students)
-- ============================================
CREATE TABLE IF NOT EXISTS estudiantes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    edad INTEGER NOT NULL,
    fecha_nacimiento DATE,
    nivel_educativo VARCHAR(50), -- IB Diploma, IGCSE, Primer grado, etc.
    foto_perfil VARCHAR(255),
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    activo BOOLEAN DEFAULT 1
);

-- ============================================
-- TABLA: Profesores (Professors)
-- ============================================
CREATE TABLE IF NOT EXISTS profesores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    especialidad VARCHAR(100), -- Matemáticas, Ciencias, etc.
    foto_perfil VARCHAR(255),
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    activo BOOLEAN DEFAULT 1
);

-- ============================================
-- TABLA: Materias (Subjects)
-- ============================================
CREATE TABLE IF NOT EXISTS materias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre VARCHAR(100) NOT NULL, -- Álgebra, Geometría, Cálculo, etc.
    descripcion TEXT,
    nivel VARCHAR(50), -- IB, IGCSE, Primer grado, etc.
    creditos INTEGER DEFAULT 0
);

-- ============================================
-- TABLA: Syllabus
-- ============================================
CREATE TABLE IF NOT EXISTS syllabus (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    materia_id INTEGER NOT NULL,
    profesor_id INTEGER NOT NULL,
    titulo VARCHAR(200) NOT NULL,
    descripcion TEXT,
    objetivos TEXT,
    contenido TEXT,
    metodologia TEXT,
    evaluacion TEXT,
    bibliografia TEXT,
    año_academico VARCHAR(20),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (materia_id) REFERENCES materias(id),
    FOREIGN KEY (profesor_id) REFERENCES profesores(id)
);

-- ============================================
-- TABLA: Calendario de Clases (Class Schedule)
-- ============================================
CREATE TABLE IF NOT EXISTS clases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    materia_id INTEGER NOT NULL,
    profesor_id INTEGER NOT NULL,
    estudiante_id INTEGER NOT NULL,
    fecha DATE NOT NULL,
    hora_inicio TIME NOT NULL,
    hora_fin TIME NOT NULL,
    duracion_horas DECIMAL(4,2), -- Calculado automáticamente
    modalidad VARCHAR(20) NOT NULL, -- Presencial, Virtual
    direccion VARCHAR(255), -- Solo para presencial
    link_virtual VARCHAR(255), -- Solo para virtual
    estado VARCHAR(20) DEFAULT 'programada', -- programada, completada, cancelada
    notas_clase TEXT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (materia_id) REFERENCES materias(id),
    FOREIGN KEY (profesor_id) REFERENCES profesores(id),
    FOREIGN KEY (estudiante_id) REFERENCES estudiantes(id)
);

-- ============================================
-- TABLA: Asistencia (Attendance)
-- ============================================
CREATE TABLE IF NOT EXISTS asistencia (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    clase_id INTEGER NOT NULL,
    estudiante_id INTEGER NOT NULL,
    estado VARCHAR(20) NOT NULL, -- Presente, Ausente, Tardanza
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (clase_id) REFERENCES clases(id),
    FOREIGN KEY (estudiante_id) REFERENCES estudiantes(id)
);

-- ============================================
-- TABLA: Notas Escolares (Grades)
-- ============================================
CREATE TABLE IF NOT EXISTS notas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    estudiante_id INTEGER NOT NULL,
    materia_id INTEGER NOT NULL,
    tipo_evaluacion VARCHAR(50) NOT NULL, -- Tarea, Examen, Proyecto, Participación
    titulo VARCHAR(200),
    calificacion DECIMAL(5,2) NOT NULL,
    calificacion_maxima DECIMAL(5,2) DEFAULT 100,
    porcentaje DECIMAL(5,2), -- Calculado automáticamente
    fecha_evaluacion DATE NOT NULL,
    trimestre VARCHAR(20),
    comentarios TEXT,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (estudiante_id) REFERENCES estudiantes(id),
    FOREIGN KEY (materia_id) REFERENCES materias(id)
);

-- ============================================
-- TABLA: Horas Acumuladas por Estudiante
-- ============================================
CREATE TABLE IF NOT EXISTS horas_estudiante (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    estudiante_id INTEGER NOT NULL,
    materia_id INTEGER NOT NULL,
    total_horas DECIMAL(6,2) DEFAULT 0,
    mes VARCHAR(7), -- YYYY-MM
    año INTEGER,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (estudiante_id) REFERENCES estudiantes(id),
    FOREIGN KEY (materia_id) REFERENCES materias(id)
);

-- ============================================
-- TABLA: Reportes de Clase del Profesor
-- ============================================
CREATE TABLE IF NOT EXISTS reportes_clase (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    clase_id INTEGER NOT NULL,
    profesor_id INTEGER NOT NULL,
    estudiante_id INTEGER NOT NULL,
    tema_cubierto TEXT NOT NULL,
    objetivos_cumplidos TEXT,
    desempeño_estudiante TEXT,
    areas_mejora TEXT,
    tareas_asignadas TEXT,
    observaciones TEXT,
    fecha_reporte TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (clase_id) REFERENCES clases(id),
    FOREIGN KEY (profesor_id) REFERENCES profesores(id),
    FOREIGN KEY (estudiante_id) REFERENCES estudiantes(id)
);

-- ============================================
-- TABLA: Metacognición del Estudiante
-- ============================================
CREATE TABLE IF NOT EXISTS metacognicion (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    estudiante_id INTEGER NOT NULL,
    clase_id INTEGER,
    fecha DATE NOT NULL,
    
    -- Autoevaluación
    comprension_tema INTEGER CHECK(comprension_tema BETWEEN 1 AND 5),
    dificultad_percibida INTEGER CHECK(dificultad_percibida BETWEEN 1 AND 5),
    confianza_nivel INTEGER CHECK(confianza_nivel BETWEEN 1 AND 5),
    
    -- Reflexión
    que_aprendi TEXT,
    que_fue_dificil TEXT,
    que_estrategias_use TEXT,
    como_mejorar TEXT,
    
    -- Emocional
    estado_animo VARCHAR(50), -- Motivado, Frustrado, Confiado, Ansioso
    nivel_estres INTEGER CHECK(nivel_estres BETWEEN 1 AND 5),
    
    -- Tiempo y esfuerzo
    tiempo_estudio_horas DECIMAL(4,2),
    esfuerzo_percibido INTEGER CHECK(esfuerzo_percibido BETWEEN 1 AND 5),
    
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (estudiante_id) REFERENCES estudiantes(id),
    FOREIGN KEY (clase_id) REFERENCES clases(id)
);

-- ============================================
-- TABLA: Métricas Objetivas del Estudiante
-- ============================================
CREATE TABLE IF NOT EXISTS metricas_objetivas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    estudiante_id INTEGER NOT NULL,
    fecha DATE NOT NULL,
    
    -- Métricas de Autonomía
    autonomia_porcentaje DECIMAL(5,2), -- 0-100
    solicitudes_ayuda INTEGER DEFAULT 0,
    tiempo_sin_ayuda_minutos INTEGER DEFAULT 0,
    
    -- Métricas de Fluidez
    fluidez_porcentaje DECIMAL(5,2), -- 0-100
    velocidad_respuesta_segundos DECIMAL(6,2),
    precision_porcentaje DECIMAL(5,2),
    
    -- Métricas de Resiliencia
    resiliencia_porcentaje DECIMAL(5,2), -- 0-100
    intentos_antes_exito INTEGER DEFAULT 0,
    persistencia_score DECIMAL(5,2),
    
    -- Racha
    racha_dias_consecutivos INTEGER DEFAULT 0,
    ultima_actividad DATE,
    
    -- Desempeño general
    nivel_dominio VARCHAR(50), -- Principiante, Intermedio, Avanzado, Experto
    progreso_semanal DECIMAL(5,2),
    promedio_general DECIMAL(5,2),
    
    -- Engagement
    tiempo_sesion_minutos INTEGER,
    sesiones_completadas INTEGER DEFAULT 0,
    ejercicios_completados INTEGER DEFAULT 0,
    
    fecha_calculo TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (estudiante_id) REFERENCES estudiantes(id)
);

-- ============================================
-- TABLA: Estilo Cognitivo del Estudiante
-- ============================================
CREATE TABLE IF NOT EXISTS estilo_cognitivo (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    estudiante_id INTEGER NOT NULL,
    tipo_estilo VARCHAR(50) NOT NULL, -- Reflexivo, Impulsivo, Analítico, Global
    nivel_intensidad INTEGER CHECK(nivel_intensidad BETWEEN 1 AND 5),
    observaciones TEXT,
    fecha_evaluacion DATE NOT NULL,
    evaluado_por INTEGER, -- profesor_id
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (estudiante_id) REFERENCES estudiantes(id),
    FOREIGN KEY (evaluado_por) REFERENCES profesores(id)
);

-- ============================================
-- TABLA: Objetivos de Aprendizaje
-- ============================================
CREATE TABLE IF NOT EXISTS objetivos_aprendizaje (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    estudiante_id INTEGER NOT NULL,
    materia_id INTEGER NOT NULL,
    objetivo TEXT NOT NULL,
    descripcion TEXT,
    fecha_inicio DATE NOT NULL,
    fecha_objetivo DATE,
    estado VARCHAR(20) DEFAULT 'en_progreso', -- en_progreso, completado, cancelado
    progreso_porcentaje DECIMAL(5,2) DEFAULT 0,
    fecha_completado DATE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (estudiante_id) REFERENCES estudiantes(id),
    FOREIGN KEY (materia_id) REFERENCES materias(id)
);

-- ============================================
-- TABLA: Comunicación Profesor-Estudiante
-- ============================================
CREATE TABLE IF NOT EXISTS mensajes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    remitente_tipo VARCHAR(20) NOT NULL, -- profesor, estudiante
    remitente_id INTEGER NOT NULL,
    destinatario_tipo VARCHAR(20) NOT NULL,
    destinatario_id INTEGER NOT NULL,
    asunto VARCHAR(200),
    mensaje TEXT NOT NULL,
    leido BOOLEAN DEFAULT 0,
    fecha_lectura TIMESTAMP,
    fecha_envio TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- ÍNDICES para optimizar consultas
-- ============================================
CREATE INDEX idx_estudiante_email ON estudiantes(email);
CREATE INDEX idx_profesor_email ON profesores(email);
CREATE INDEX idx_clases_fecha ON clases(fecha);
CREATE INDEX idx_clases_estudiante ON clases(estudiante_id);
CREATE INDEX idx_notas_estudiante ON notas(estudiante_id);
CREATE INDEX idx_metricas_estudiante_fecha ON metricas_objetivas(estudiante_id, fecha);
CREATE INDEX idx_metacognicion_estudiante ON metacognicion(estudiante_id);
CREATE INDEX idx_reportes_estudiante ON reportes_clase(estudiante_id);

-- ============================================
-- VISTAS útiles
-- ============================================

-- Vista: Resumen de estudiante
CREATE VIEW IF NOT EXISTS vista_resumen_estudiante AS
SELECT 
    e.id,
    e.nombre || ' ' || e.apellido AS nombre_completo,
    e.edad,
    e.nivel_educativo,
    COUNT(DISTINCT c.id) AS total_clases,
    SUM(c.duracion_horas) AS horas_totales,
    AVG(n.porcentaje) AS promedio_notas,
    m.autonomia_porcentaje,
    m.fluidez_porcentaje,
    m.resiliencia_porcentaje,
    m.racha_dias_consecutivos
FROM estudiantes e
LEFT JOIN clases c ON e.id = c.estudiante_id AND c.estado = 'completada'
LEFT JOIN notas n ON e.id = n.estudiante_id
LEFT JOIN (
    SELECT estudiante_id, autonomia_porcentaje, fluidez_porcentaje, 
           resiliencia_porcentaje, racha_dias_consecutivos
    FROM metricas_objetivas
    WHERE fecha = (SELECT MAX(fecha) FROM metricas_objetivas WHERE estudiante_id = metricas_objetivas.estudiante_id)
) m ON e.id = m.estudiante_id
GROUP BY e.id;

-- Vista: Calendario completo
CREATE VIEW IF NOT EXISTS vista_calendario_completo AS
SELECT 
    c.id,
    c.fecha,
    c.hora_inicio,
    c.hora_fin,
    c.duracion_horas,
    c.modalidad,
    c.direccion,
    e.nombre || ' ' || e.apellido AS estudiante,
    p.nombre || ' ' || p.apellido AS profesor,
    m.nombre AS materia,
    m.nivel,
    c.estado,
    a.estado AS asistencia
FROM clases c
JOIN estudiantes e ON c.estudiante_id = e.id
JOIN profesores p ON c.profesor_id = p.id
JOIN materias m ON c.materia_id = m.id
LEFT JOIN asistencia a ON c.id = a.clase_id AND e.id = a.estudiante_id;
