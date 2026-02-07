# 📊 Study Buddy - Base de Datos

## Descripción General

Base de datos completa para gestionar toda la información del sistema Study Buddy, incluyendo estudiantes, profesores, clases, calificaciones, reportes y métricas objetivas de aprendizaje.

---

## 🗂️ Estructura de la Base de Datos

### 1. **Estudiantes** (`estudiantes`)
Información básica de los estudiantes.

**Campos:**
- `id`: ID único
- `nombre`, `apellido`: Nombres del estudiante
- `email`: Email único
- `edad`: Edad actual
- `fecha_nacimiento`: Fecha de nacimiento
- `nivel_educativo`: IB Diploma, IGCSE, Primer grado, etc.
- `foto_perfil`: URL de la foto
- `fecha_registro`, `activo`

---

### 2. **Profesores** (`profesores`)
Información de los profesores/tutores.

**Campos:**
- `id`, `nombre`, `apellido`, `email`
- `especialidad`: Matemáticas, Ciencias, etc.
- `foto_perfil`, `fecha_registro`, `activo`

---

### 3. **Materias** (`materias`)
Catálogo de materias/asignaturas.

**Campos:**
- `id`, `nombre`: Álgebra, Geometría, Cálculo, etc.
- `descripcion`, `nivel`, `creditos`

---

### 4. **Syllabus** (`syllabus`)
Programas de estudio para cada materia.

**Campos:**
- `id`, `materia_id`, `profesor_id`
- `titulo`, `descripcion`, `objetivos`
- `contenido`, `metodologia`, `evaluacion`
- `bibliografia`, `año_academico`

---

### 5. **Calendario de Clases** (`clases`)
**Almacena todas las fechas y horarios de clases.**

**Campos:**
- `id`, `materia_id`, `profesor_id`, `estudiante_id`
- `fecha`, `hora_inicio`, `hora_fin`
- `duracion_horas`: Calculado automáticamente
- `modalidad`: Presencial o Virtual
- `direccion`: Para clases presenciales
- `link_virtual`: Para clases virtuales
- `estado`: programada, completada, cancelada
- `notas_clase`

**Ejemplo:**
```python
db.create_class(
    materia_id=1,
    profesor_id=1,
    estudiante_id=5,
    fecha='2026-02-10',
    hora_inicio='14:00',
    hora_fin='16:00',
    modalidad='Presencial',
    direccion='Calle Berlin 363, Miraflores'
)
```

---

### 6. **Asistencia** (`asistencia`)
Registro de asistencia de estudiantes.

**Campos:**
- `clase_id`, `estudiante_id`
- `estado`: Presente, Ausente, Tardanza

---

### 7. **Notas Escolares** (`notas`)
**Almacena todas las calificaciones de los estudiantes.**

**Campos:**
- `id`, `estudiante_id`, `materia_id`
- `tipo_evaluacion`: Tarea, Examen, Proyecto, Participación
- `titulo`, `calificacion`, `calificacion_maxima`
- `porcentaje`: Calculado automáticamente
- `fecha_evaluacion`, `trimestre`, `comentarios`

**Ejemplo:**
```python
db.add_grade(
    estudiante_id=5,
    materia_id=1,
    tipo_evaluacion='Examen',
    titulo='Examen Final Álgebra',
    calificacion=85,
    calificacion_maxima=100,
    fecha_evaluacion='2026-02-15',
    trimestre='Q1'
)
```

---

### 8. **Horas Acumuladas** (`horas_estudiante`)
**Rastrea las horas totales que cada estudiante ha recibido.**

**Campos:**
- `estudiante_id`, `materia_id`
- `total_horas`: Total acumulado
- `mes`, `año`

**Calculado automáticamente** desde la tabla `clases`.

---

### 9. **Reportes de Clase** (`reportes_clase`)
**Los profesores crean reportes después de cada clase.**

**Campos:**
- `clase_id`, `profesor_id`, `estudiante_id`
- `tema_cubierto`: Qué se enseñó
- `objetivos_cumplidos`
- `desempeño_estudiante`: Descripción del desempeño
- `areas_mejora`: Áreas que necesitan trabajo
- `tareas_asignadas`
- `observaciones`

**Ejemplo:**
```python
db.create_class_report(
    clase_id=123,
    profesor_id=1,
    estudiante_id=5,
    tema_cubierto='Ecuaciones cuadráticas',
    desempeño_estudiante='Excelente comprensión, resolvió 8/10 problemas',
    areas_mejora='Necesita practicar discriminante negativo',
    tareas_asignadas='Ejercicios 15-20 del libro'
)
```

---

### 10. **Metacognición** (`metacognicion`)
**Reflexión del estudiante sobre su propio aprendizaje.**

**Campos:**
- `estudiante_id`, `clase_id`, `fecha`
- `comprension_tema` (1-5)
- `dificultad_percibida` (1-5)
- `confianza_nivel` (1-5)
- `que_aprendi`, `que_fue_dificil`
- `que_estrategias_use`, `como_mejorar`
- `estado_animo`: Motivado, Frustrado, Confiado, Ansioso
- `nivel_estres` (1-5)
- `tiempo_estudio_horas`, `esfuerzo_percibido` (1-5)

**Ejemplo:**
```python
db.save_metacognition(
    estudiante_id=5,
    fecha='2026-02-10',
    comprension_tema=4,
    dificultad_percibida=3,
    confianza_nivel=4,
    que_aprendi='Aprendí a resolver ecuaciones cuadráticas con fórmula general',
    que_fue_dificil='Me costó identificar los coeficientes a, b, c',
    estado_animo='Confiado',
    nivel_estres=2
)
```

---

### 11. **Métricas Objetivas** (`metricas_objetivas`)
**Las métricas que definimos para medir progreso objetivamente.**

**Campos principales:**

#### Autonomía
- `autonomia_porcentaje` (0-100)
- `solicitudes_ayuda`: Número de veces que pidió ayuda
- `tiempo_sin_ayuda_minutos`

#### Fluidez
- `fluidez_porcentaje` (0-100)
- `velocidad_respuesta_segundos`
- `precision_porcentaje`

#### Resiliencia
- `resiliencia_porcentaje` (0-100)
- `intentos_antes_exito`
- `persistencia_score`

#### Racha
- `racha_dias_consecutivos`
- `ultima_actividad`

#### Desempeño General
- `nivel_dominio`: Principiante, Intermedio, Avanzado, Experto
- `progreso_semanal`
- `promedio_general`

#### Engagement
- `tiempo_sesion_minutos`
- `sesiones_completadas`
- `ejercicios_completados`

**Ejemplo:**
```python
db.save_metrics(
    estudiante_id=5,
    fecha='2026-02-10',
    autonomia=45,
    fluidez=62,
    resiliencia=78,
    racha_dias=3,
    solicitudes_ayuda=8,
    velocidad_respuesta=12.5,
    precision=85,
    tiempo_sesion=90,
    ejercicios_completados=15
)
```

---

### 12. **Estilo Cognitivo** (`estilo_cognitivo`)
Perfiles cognitivos de los estudiantes.

**Campos:**
- `tipo_estilo`: Reflexivo, Impulsivo, Analítico, Global
- `nivel_intensidad` (1-5)
- `fecha_evaluacion`, `evaluado_por`

---

### 13. **Objetivos de Aprendizaje** (`objetivos_aprendizaje`)
Metas y objetivos de cada estudiante.

**Campos:**
- `estudiante_id`, `materia_id`
- `objetivo`, `descripcion`
- `fecha_inicio`, `fecha_objetivo`
- `estado`: en_progreso, completado, cancelado
- `progreso_porcentaje`

---

### 14. **Mensajes** (`mensajes`)
Comunicación entre profesores y estudiantes.

**Campos:**
- `remitente_tipo`, `remitente_id`
- `destinatario_tipo`, `destinatario_id`
- `asunto`, `mensaje`, `leido`

---

## 🔍 Vistas Útiles

### `vista_resumen_estudiante`
Resumen completo de cada estudiante incluyendo:
- Total de clases
- Horas totales
- Promedio de notas
- Métricas actuales (autonomía, fluidez, resiliencia, racha)

### `vista_calendario_completo`
Vista completa del calendario con toda la información:
- Datos de la clase
- Nombre del estudiante y profesor
- Materia y nivel
- Estado y asistencia

---

## 🚀 Uso Rápido

### Inicializar la base de datos

```python
from database import StudyBuddyDB

db = StudyBuddyDB('studybuddy.db')
db.initialize_database('database_schema.sql')
```

### Crear un estudiante

```python
student_id = db.create_student(
    nombre='Juan',
    apellido='Martinez',
    email='juan.martinez@email.com',
    edad=15,
    nivel_educativo='IB Diploma',
    fecha_nacimiento='2011-03-15'
)
```

### Obtener resumen del estudiante

```python
resumen = db.get_student_summary(student_id)
print(f"Horas totales: {resumen['horas_totales']}")
print(f"Promedio: {resumen['promedio_notas']}")
print(f"Autonomía: {resumen['autonomia_porcentaje']}%")
```

### Consultar calendario

```python
clases = db.get_student_schedule(
    student_id=5,
    fecha_inicio='2026-02-01',
    fecha_fin='2026-02-28'
)

for clase in clases:
    print(f"{clase['fecha']} - {clase['materia']} con {clase['profesor']}")
```

---

## 📝 Integración con Backend

Para integrar con el backend Flask:

```python
# En app.py
from database import StudyBuddyDB

db = StudyBuddyDB()

@app.route('/api/students/<int:student_id>/summary', methods=['GET'])
def get_student_summary(student_id):
    summary = db.get_student_summary(student_id)
    return jsonify(summary)

@app.route('/api/students/<int:student_id>/metrics', methods=['GET'])
def get_student_metrics(student_id):
    metrics = db.get_latest_metrics(student_id)
    return jsonify(metrics)
```

---

## 🔄 Actualización Automática de Horas

Las horas se calculan automáticamente:

```python
# Después de completar una clase
db.update_student_hours(student_id)

# Consultar total
hours = db.get_student_total_hours(student_id)
print(f"Total horas: {hours['total_horas_general']}")
```

---

## 📊 Queries Útiles

```sql
-- Estudiantes con más horas este mes
SELECT e.nombre, SUM(c.duracion_horas) as horas
FROM estudiantes e
JOIN clases c ON e.id = c.estudiante_id
WHERE strftime('%Y-%m', c.fecha) = '2026-02'
AND c.estado = 'completada'
GROUP BY e.id
ORDER BY horas DESC;

-- Promedio de notas por estudiante y materia
SELECT e.nombre, m.nombre as materia, AVG(n.porcentaje) as promedio
FROM notas n
JOIN estudiantes e ON n.estudiante_id = e.id
JOIN materias m ON n.materia_id = m.id
GROUP BY e.id, m.id;

-- Racha actual de todos los estudiantes
SELECT e.nombre, mo.racha_dias_consecutivos, mo.fecha
FROM estudiantes e
JOIN metricas_objetivas mo ON e.id = mo.estudiante_id
WHERE mo.fecha = (
    SELECT MAX(fecha) 
    FROM metricas_objetivas 
    WHERE estudiante_id = e.id
);
```

---

## 🎯 Próximos Pasos

1. ✅ Ejecutar `python database.py` para crear la base de datos
2. ✅ Integrar con el backend Flask
3. ✅ Crear APIs REST para cada entidad
4. ✅ Conectar con el frontend
5. ✅ Implementar dashboard con visualizaciones
