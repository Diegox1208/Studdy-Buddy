"""
Study Buddy - Database Manager
Manages SQLite database for storing student information, classes, grades, and metrics
"""

import sqlite3
import os
from datetime import datetime, date
from typing import Optional, List, Dict, Any

class StudyBuddyDB:
    def __init__(self, db_path: str = 'studybuddy.db'):
        """Initialize database connection"""
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        
    def connect(self):
        """Connect to the database"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        self.cursor = self.conn.cursor()
        
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            
    def initialize_database(self, schema_file: str = 'database_schema.sql'):
        """Initialize database with schema"""
        self.connect()
        
        # Read and execute schema
        with open(schema_file, 'r', encoding='utf-8') as f:
            schema = f.read()
            self.cursor.executescript(schema)
            self.conn.commit()
            
        print("✅ Database initialized successfully!")
        self.close()
        
    # ============================================
    # ESTUDIANTES (Students)
    # ============================================
    
    def create_student(self, nombre: str, apellido: str, email: str, edad: int, 
                      nivel_educativo: str, fecha_nacimiento: Optional[str] = None,
                      foto_perfil: Optional[str] = None) -> int:
        """Create a new student"""
        self.connect()
        query = """
        INSERT INTO estudiantes (nombre, apellido, email, edad, nivel_educativo, 
                                fecha_nacimiento, foto_perfil)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        self.cursor.execute(query, (nombre, apellido, email, edad, nivel_educativo,
                                   fecha_nacimiento, foto_perfil))
        self.conn.commit()
        student_id = self.cursor.lastrowid
        self.close()
        return student_id
        
    def get_student(self, student_id: int) -> Optional[Dict]:
        """Get student by ID"""
        self.connect()
        query = "SELECT * FROM estudiantes WHERE id = ?"
        self.cursor.execute(query, (student_id,))
        result = self.cursor.fetchone()
        self.close()
        return dict(result) if result else None
        
    def get_all_students(self, activo: bool = True) -> List[Dict]:
        """Get all students"""
        self.connect()
        query = "SELECT * FROM estudiantes WHERE activo = ?"
        self.cursor.execute(query, (activo,))
        results = [dict(row) for row in self.cursor.fetchall()]
        self.close()
        return results
        
    def update_student(self, student_id: int, **kwargs) -> bool:
        """Update student information"""
        self.connect()
        fields = ', '.join([f"{k} = ?" for k in kwargs.keys()])
        query = f"UPDATE estudiantes SET {fields} WHERE id = ?"
        values = list(kwargs.values()) + [student_id]
        self.cursor.execute(query, values)
        self.conn.commit()
        success = self.cursor.rowcount > 0
        self.close()
        return success
        
    # ============================================
    # PROFESORES (Professors)
    # ============================================
    
    def create_professor(self, nombre: str, apellido: str, email: str,
                        especialidad: Optional[str] = None,
                        foto_perfil: Optional[str] = None) -> int:
        """Create a new professor"""
        self.connect()
        query = """
        INSERT INTO profesores (nombre, apellido, email, especialidad, foto_perfil)
        VALUES (?, ?, ?, ?, ?)
        """
        self.cursor.execute(query, (nombre, apellido, email, especialidad, foto_perfil))
        self.conn.commit()
        professor_id = self.cursor.lastrowid
        self.close()
        return professor_id
        
    def get_professor(self, professor_id: int) -> Optional[Dict]:
        """Get professor by ID"""
        self.connect()
        query = "SELECT * FROM profesores WHERE id = ?"
        self.cursor.execute(query, (professor_id,))
        result = self.cursor.fetchone()
        self.close()
        return dict(result) if result else None
        
    # ============================================
    # CLASES (Classes)
    # ============================================
    
    def create_class(self, materia_id: int, profesor_id: int, estudiante_id: int,
                    fecha: str, hora_inicio: str, hora_fin: str,
                    modalidad: str, direccion: Optional[str] = None,
                    link_virtual: Optional[str] = None) -> int:
        """Create a new class"""
        self.connect()
        
        # Calculate duration
        from datetime import datetime
        t1 = datetime.strptime(hora_inicio, '%H:%M')
        t2 = datetime.strptime(hora_fin, '%H:%M')
        duracion = (t2 - t1).seconds / 3600
        
        query = """
        INSERT INTO clases (materia_id, profesor_id, estudiante_id, fecha,
                           hora_inicio, hora_fin, duracion_horas, modalidad,
                           direccion, link_virtual)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        self.cursor.execute(query, (materia_id, profesor_id, estudiante_id, fecha,
                                   hora_inicio, hora_fin, duracion, modalidad,
                                   direccion, link_virtual))
        self.conn.commit()
        class_id = self.cursor.lastrowid
        self.close()
        return class_id
        
    def get_student_schedule(self, student_id: int, fecha_inicio: str,
                            fecha_fin: str) -> List[Dict]:
        """Get student schedule for date range"""
        self.connect()
        query = """
        SELECT * FROM vista_calendario_completo
        WHERE estudiante LIKE ? AND fecha BETWEEN ? AND ?
        ORDER BY fecha, hora_inicio
        """
        # Get student name first
        student = self.get_student(student_id)
        nombre_completo = f"{student['nombre']} {student['apellido']}"
        
        self.cursor.execute(query, (f"%{nombre_completo}%", fecha_inicio, fecha_fin))
        results = [dict(row) for row in self.cursor.fetchall()]
        self.close()
        return results
        
    # ============================================
    # NOTAS (Grades)
    # ============================================
    
    def add_grade(self, estudiante_id: int, materia_id: int, tipo_evaluacion: str,
                 calificacion: float, calificacion_maxima: float, fecha_evaluacion: str,
                 titulo: Optional[str] = None, trimestre: Optional[str] = None,
                 comentarios: Optional[str] = None) -> int:
        """Add a grade"""
        self.connect()
        
        # Calculate percentage
        porcentaje = (calificacion / calificacion_maxima) * 100
        
        query = """
        INSERT INTO notas (estudiante_id, materia_id, tipo_evaluacion, titulo,
                          calificacion, calificacion_maxima, porcentaje,
                          fecha_evaluacion, trimestre, comentarios)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        self.cursor.execute(query, (estudiante_id, materia_id, tipo_evaluacion, titulo,
                                   calificacion, calificacion_maxima, porcentaje,
                                   fecha_evaluacion, trimestre, comentarios))
        self.conn.commit()
        grade_id = self.cursor.lastrowid
        self.close()
        return grade_id
        
    def get_student_grades(self, student_id: int, materia_id: Optional[int] = None) -> List[Dict]:
        """Get all grades for a student"""
        self.connect()
        if materia_id:
            query = "SELECT * FROM notas WHERE estudiante_id = ? AND materia_id = ? ORDER BY fecha_evaluacion DESC"
            self.cursor.execute(query, (student_id, materia_id))
        else:
            query = "SELECT * FROM notas WHERE estudiante_id = ? ORDER BY fecha_evaluacion DESC"
            self.cursor.execute(query, (student_id,))
        results = [dict(row) for row in self.cursor.fetchall()]
        self.close()
        return results
        
    # ============================================
    # MÉTRICAS OBJETIVAS (Objective Metrics)
    # ============================================
    
    def save_metrics(self, estudiante_id: int, fecha: str, autonomia: float,
                    fluidez: float, resiliencia: float, racha_dias: int,
                    **kwargs) -> int:
        """Save student metrics"""
        self.connect()
        
        query = """
        INSERT INTO metricas_objetivas (
            estudiante_id, fecha, autonomia_porcentaje, fluidez_porcentaje,
            resiliencia_porcentaje, racha_dias_consecutivos,
            solicitudes_ayuda, velocidad_respuesta_segundos, precision_porcentaje,
            intentos_antes_exito, tiempo_sesion_minutos, ejercicios_completados
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        self.cursor.execute(query, (
            estudiante_id, fecha, autonomia, fluidez, resiliencia, racha_dias,
            kwargs.get('solicitudes_ayuda', 0),
            kwargs.get('velocidad_respuesta', 0),
            kwargs.get('precision', 0),
            kwargs.get('intentos_antes_exito', 0),
            kwargs.get('tiempo_sesion', 0),
            kwargs.get('ejercicios_completados', 0)
        ))
        self.conn.commit()
        metric_id = self.cursor.lastrowid
        self.close()
        return metric_id
        
    def get_latest_metrics(self, student_id: int) -> Optional[Dict]:
        """Get latest metrics for student"""
        self.connect()
        query = """
        SELECT * FROM metricas_objetivas
        WHERE estudiante_id = ?
        ORDER BY fecha DESC
        LIMIT 1
        """
        self.cursor.execute(query, (student_id,))
        result = self.cursor.fetchone()
        self.close()
        return dict(result) if result else None
        
    # ============================================
    # REPORTES DE CLASE (Class Reports)
    # ============================================
    
    def create_class_report(self, clase_id: int, profesor_id: int, estudiante_id: int,
                           tema_cubierto: str, desempeño_estudiante: str,
                           **kwargs) -> int:
        """Create a class report"""
        self.connect()
        
        query = """
        INSERT INTO reportes_clase (
            clase_id, profesor_id, estudiante_id, tema_cubierto,
            desempeño_estudiante, objetivos_cumplidos, areas_mejora,
            tareas_asignadas, observaciones
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        self.cursor.execute(query, (
            clase_id, profesor_id, estudiante_id, tema_cubierto,
            desempeño_estudiante,
            kwargs.get('objetivos_cumplidos', ''),
            kwargs.get('areas_mejora', ''),
            kwargs.get('tareas_asignadas', ''),
            kwargs.get('observaciones', '')
        ))
        self.conn.commit()
        report_id = self.cursor.lastrowid
        self.close()
        return report_id
        
    def get_student_reports(self, student_id: int, limit: int = 10) -> List[Dict]:
        """Get class reports for student"""
        self.connect()
        query = """
        SELECT r.*, p.nombre || ' ' || p.apellido AS profesor_nombre,
               c.fecha AS fecha_clase
        FROM reportes_clase r
        JOIN profesores p ON r.profesor_id = p.id
        JOIN clases c ON r.clase_id = c.id
        WHERE r.estudiante_id = ?
        ORDER BY r.fecha_reporte DESC
        LIMIT ?
        """
        self.cursor.execute(query, (student_id, limit))
        results = [dict(row) for row in self.cursor.fetchall()]
        self.close()
        return results
        
    # ============================================
    # METACOGNICIÓN (Metacognition)
    # ============================================
    
    def save_metacognition(self, estudiante_id: int, fecha: str,
                          comprension_tema: int, dificultad_percibida: int,
                          confianza_nivel: int, **kwargs) -> int:
        """Save student metacognition entry"""
        self.connect()
        
        query = """
        INSERT INTO metacognicion (
            estudiante_id, fecha, comprension_tema, dificultad_percibida,
            confianza_nivel, que_aprendi, que_fue_dificil, que_estrategias_use,
            como_mejorar, estado_animo, nivel_estres, tiempo_estudio_horas,
            esfuerzo_percibido, clase_id
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        self.cursor.execute(query, (
            estudiante_id, fecha, comprension_tema, dificultad_percibida,
            confianza_nivel,
            kwargs.get('que_aprendi', ''),
            kwargs.get('que_fue_dificil', ''),
            kwargs.get('que_estrategias_use', ''),
            kwargs.get('como_mejorar', ''),
            kwargs.get('estado_animo', ''),
            kwargs.get('nivel_estres', 3),
            kwargs.get('tiempo_estudio_horas', 0),
            kwargs.get('esfuerzo_percibido', 3),
            kwargs.get('clase_id')
        ))
        self.conn.commit()
        metacog_id = self.cursor.lastrowid
        self.close()
        return metacog_id
        
    # ============================================
    # HORAS ACUMULADAS (Accumulated Hours)
    # ============================================
    
    def update_student_hours(self, student_id: int):
        """Update accumulated hours for student"""
        self.connect()
        
        # Calculate total hours from completed classes
        query = """
        INSERT OR REPLACE INTO horas_estudiante (estudiante_id, materia_id, total_horas, mes, año)
        SELECT 
            estudiante_id,
            materia_id,
            SUM(duracion_horas) AS total_horas,
            strftime('%Y-%m', fecha) AS mes,
            CAST(strftime('%Y', fecha) AS INTEGER) AS año
        FROM clases
        WHERE estudiante_id = ? AND estado = 'completada'
        GROUP BY estudiante_id, materia_id, strftime('%Y-%m', fecha)
        """
        
        self.cursor.execute(query, (student_id,))
        self.conn.commit()
        self.close()
        
    def get_student_total_hours(self, student_id: int) -> Dict:
        """Get total hours for student"""
        self.connect()
        query = """
        SELECT 
            SUM(total_horas) AS total_horas_general,
            materia_id
        FROM horas_estudiante
        WHERE estudiante_id = ?
        GROUP BY estudiante_id
        """
        self.cursor.execute(query, (student_id,))
        result = self.cursor.fetchone()
        self.close()
        return dict(result) if result else {'total_horas_general': 0}
        
    # ============================================
    # RESUMEN DE ESTUDIANTE (Student Summary)
    # ============================================
    
    def get_student_summary(self, student_id: int) -> Optional[Dict]:
        """Get comprehensive student summary"""
        self.connect()
        query = "SELECT * FROM vista_resumen_estudiante WHERE id = ?"
        self.cursor.execute(query, (student_id,))
        result = self.cursor.fetchone()
        self.close()
        return dict(result) if result else None


# ============================================
# Example Usage
# ============================================

if __name__ == "__main__":
    # Initialize database
    db = StudyBuddyDB()
    db.initialize_database()
    
    print("\n📊 Study Buddy Database initialized successfully!")
    print("=" * 50)
    print("\nDatabase includes tables for:")
    print("✅ Estudiantes (Students)")
    print("✅ Profesores (Professors)")
    print("✅ Materias (Subjects)")
    print("✅ Syllabus")
    print("✅ Calendario de Clases")
    print("✅ Notas Escolares")
    print("✅ Horas Acumuladas")
    print("✅ Reportes de Clase")
    print("✅ Metacognición")
    print("✅ Métricas Objetivas")
    print("✅ Estilo Cognitivo")
    print("✅ Objetivos de Aprendizaje")
    print("✅ Comunicación (Mensajes)")
