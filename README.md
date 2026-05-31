# PG / Hostel Visitor Log System
**21CSC205P – Database Management Systems | SRM IST**
> Anandha Ruban I [RA2411042010013] · Praveen M [RA2411042010026]
> Guide: Mr. Balachander S

---

## 📁 Project Structure

```
hostel-visitor-system/
├── backend/
│   ├── app.py              ← Python Flask backend (ALL API logic)
│   ├── requirements.txt    ← Python dependencies
│   └── hostel_visitor.db   ← SQLite DB (auto-created on first run)
└── frontend/
    └── index.html          ← Single-file frontend (HTML + CSS + JS)
```

---

## ⚙️ Setup & Run

### Step 1 – Install Python dependencies
```bash
cd backend
pip install -r requirements.txt
```

### Step 2 – Start the backend server
```bash
python app.py
```
The server starts at: **http://127.0.0.1:5000**
Sample data is auto-seeded on first run.

### Step 3 – Open the frontend
Just open `frontend/index.html` in your browser (double-click or drag into Chrome/Firefox).

---

## 🗄️ Database Schema

```sql
STUDENT(student_id PK, name, room_no, phone UNIQUE)
VISITOR(visitor_id PK, name, phone, relation)
VISIT_LOG(log_id PK, visit_date, in_time, student_id FK, visitor_id FK)
```

---

## 🔌 REST API Endpoints

| Method | Endpoint              | Description                |
|--------|-----------------------|----------------------------|
| GET    | /api/students         | Get all students           |
| POST   | /api/students         | Add a student              |
| PUT    | /api/students/:id     | Update student             |
| DELETE | /api/students/:id     | Delete student + logs      |
| GET    | /api/visitors         | Get all visitors           |
| POST   | /api/visitors         | Add a visitor              |
| DELETE | /api/visitors/:id     | Delete visitor + logs      |
| GET    | /api/visits           | Get all visit logs (JOINed)|
| POST   | /api/visits           | Log a new visit            |
| DELETE | /api/visits/:id       | Delete a visit log         |
| GET    | /api/stats            | Dashboard stats (aggregates)|
| GET    | /api/search?q=...     | Search visit records        |
| GET    | /api/health           | Server health check         |
