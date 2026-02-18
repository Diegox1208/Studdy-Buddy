# 📅 Study Buddy - Class Booking System Setup

## 🎯 Overview

The booking system allows students to:
1. Click "Tomar Clase" button
2. Select subject, date, and time
3. Submit the booking
4. **Data is saved to database and appears on professor's calendar**

---

## 🚀 Setup Instructions

### 1. Initialize Database with Test Data

```bash
cd backend
python init_test_data.py
```

This creates:
- ✅ 1 test student (Alex Johnson, ID: 1)
- ✅ 3 test professors
- ✅ 9 subjects (Matemáticas, Física, etc.)

### 2. Start Backend Server

```bash
python app.py
```

Server runs on: `http://localhost:5000`

### 3. Open Student Interface

Open `frontend/student_interface.html` in browser or run:

```bash
cd frontend
python -m http.server 8000
```

Then visit: `http://localhost:8000/student_interface.html`

---

## 📊 How It Works

### Student Side (student_interface.html):

1. Student clicks **"Tomar Clase"** button
2. Modal pops up with filters:
   - Elige Materia
   - Fecha
   - Hora Inicio
   - Hora Fin
3. Student clicks **"¡Estoy Listo!"**
4. Frontend calls `POST /api/bookings` with data
5. Backend saves to database `clases` table
6. Success message shows with booking details

### Professor Side (professor_dashboard.html):

The professor dashboard can fetch bookings with:

```javascript
// Fetch all bookings for a specific professor
fetch('http://localhost:5000/api/bookings?profesor_id=1')
    .then(res => res.json())
    .then(bookings => {
        // Display on calendar
        console.log(bookings);
    });
```

Each booking includes:
- `id` - Class ID
- `fecha` - Date
- `hora_inicio` - Start time
- `hora_fin` - End time
- `estado` - Status (programada, completada, cancelada)
- `materia` - Subject name
- `estudiante` - Student name
- `profesor` - Professor name

---

## 🗄️ Database Schema

### Table: `clases` (Classes)

```sql
CREATE TABLE clases (
    id INTEGER PRIMARY KEY,
    materia_id INTEGER,
    profesor_id INTEGER,
    estudiante_id INTEGER,
    fecha DATE,
    hora_inicio TIME,
    hora_fin TIME,
    duracion_horas DECIMAL,
    modalidad VARCHAR(20),  -- Virtual, Presencial
    direccion VARCHAR(255),
    link_virtual VARCHAR(255),
    estado VARCHAR(20),     -- programada, completada, cancelada
    notas_clase TEXT
);
```

---

## 🔧 API Endpoints

### POST `/api/bookings`

Create a new class booking.

**Request:**
```json
{
    "estudiante_id": 1,
    "materia": "matematicas",
    "fecha": "2026-02-20",
    "hora_inicio": "14:00",
    "hora_fin": "16:00",
    "modalidad": "Virtual",
    "link_virtual": "https://meet.google.com/xxx"
}
```

**Response:**
```json
{
    "success": true,
    "class_id": 123,
    "message": "Clase programada exitosamente",
    "details": {
        "materia": "Matemáticas",
        "fecha": "2026-02-20",
        "hora_inicio": "14:00",
        "hora_fin": "16:00",
        "profesor_id": 1
    }
}
```

### GET `/api/bookings`

Get all bookings (optionally filtered).

**Query Parameters:**
- `estudiante_id` - Filter by student
- `profesor_id` - Filter by professor

**Response:**
```json
[
    {
        "id": 123,
        "fecha": "2026-02-20",
        "hora_inicio": "14:00",
        "hora_fin": "16:00",
        "estado": "programada",
        "modalidad": "Virtual",
        "materia": "Matemáticas",
        "estudiante": "Alex Johnson",
        "profesor": "María García"
    }
]
```

---

## 🎨 Frontend Integration

### Update Student Interface Config

In `frontend/student_interface.html`, the booking function uses:

```javascript
// Line 739 - Change student_id based on logged-in user
const bookingData = {
    estudiante_id: 1,  // TODO: Get from session
    materia: materia,
    fecha: fecha,
    hora_inicio: horaInicio,
    hora_fin: horaFin
};
```

### Update Professor Dashboard

Add this to `professor_dashboard.html` to show bookings:

```javascript
// Fetch bookings for this professor
async function loadCalendar() {
    const response = await fetch('http://localhost:5000/api/bookings?profesor_id=1');
    const bookings = await response.json();
    
    // Display on calendar
    bookings.forEach(booking => {
        addEventToCalendar({
            date: booking.fecha,
            time: booking.hora_inicio,
            title: booking.materia,
            student: booking.estudiante,
            type: 'class'
        });
    });
}
```

---

## 🧪 Testing

### Test the full flow:

1. **Start backend**: `python app.py`
2. **Open student interface**: `http://localhost:8000/student_interface.html`
3. **Click "Tomar Clase"**
4. **Fill form:**
   - Materia: Matemáticas
   - Fecha: Tomorrow
   - Hora: 14:00 - 16:00
5. **Click "¡Estoy Listo!"**
6. **Verify success message**
7. **Check database:**
   ```bash
   sqlite3 studybuddy.db
   SELECT * FROM clases;
   ```

### Expected result:
```
id|materia_id|profesor_id|estudiante_id|fecha|hora_inicio|hora_fin|...
1|1|1|1|2026-02-20|14:00|16:00|...
```

---

## 🔄 Next Steps

### For Production:

1. **Authentication**: Replace hardcoded `estudiante_id: 1` with session data
2. **Smart Matching**: Add algorithm to match students with best available professor
3. **Notifications**: Send email/SMS to professor when new booking created
4. **Calendar Integration**: Add Google Calendar sync
5. **Payment**: Integrate payment gateway before booking confirmation
6. **Availability**: Check professor availability before booking

### Database on Railway:

Once you deploy backend to Railway:

1. Update frontend API URL:
   ```javascript
   const API_URL = 'https://studdybuddy-production-5a70.up.railway.app';
   ```

2. Initialize Railway database:
   ```bash
   railway run python init_test_data.py
   ```

---

## 📞 Support

If you encounter issues:
- Check backend is running: `http://localhost:5000/health`
- Check browser console for errors (F12)
- Verify database exists: `ls backend/studybuddy.db`

**Backend logs** show all API requests in real-time.

---

## ✅ Summary

✅ Backend API ready (`/api/bookings`)
✅ Frontend form connected to API
✅ Database schema includes `clases` table
✅ Test data initialization script created
✅ Professor can fetch bookings via API

**The booking data now flows:**
Student Form → Backend API → Database → Professor Calendar

🎉 **System is ready to use!**
