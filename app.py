"""
PG / Hostel Visitor Log System - Backend (Python Flask)
Database: SQLite (portable) | ORM: SQLAlchemy
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date, time
import os

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests from frontend

# ─────────────────────────────────────────
#  DATABASE CONFIGURATION
# ─────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(BASE_DIR, "hostel_visitor.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# ─────────────────────────────────────────
#  DATABASE MODELS (Relational Schema)
# ─────────────────────────────────────────

class Student(db.Model):
    """
    STUDENT(student_id PK, name, room_no, phone)
    One student can receive multiple visits (One-to-Many with VISIT_LOG)
    """
    __tablename__ = 'STUDENT'

    student_id = db.Column(db.Integer, primary_key=True)
    name       = db.Column(db.String(50), nullable=False)
    room_no    = db.Column(db.String(10), nullable=False)
    phone      = db.Column(db.String(15), nullable=False, unique=True)

    # Relationship
    visits = db.relationship('VisitLog', backref='student', lazy=True,
                             cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'student_id': self.student_id,
            'name':       self.name,
            'room_no':    self.room_no,
            'phone':      self.phone
        }


class Visitor(db.Model):
    """
    VISITOR(visitor_id PK, name, phone, relation)
    One visitor can make multiple visits (One-to-Many with VISIT_LOG)
    """
    __tablename__ = 'VISITOR'

    visitor_id = db.Column(db.Integer, primary_key=True)
    name       = db.Column(db.String(50), nullable=False)
    phone      = db.Column(db.String(15), nullable=False)
    relation   = db.Column(db.String(30), nullable=False)

    # Relationship
    visits = db.relationship('VisitLog', backref='visitor', lazy=True,
                             cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'visitor_id': self.visitor_id,
            'name':       self.name,
            'phone':      self.phone,
            'relation':   self.relation
        }


class VisitLog(db.Model):
    """
    VISIT_LOG(log_id PK, visit_date, in_time, student_id FK, visitor_id FK)
    Associative entity linking STUDENT and VISITOR
    """
    __tablename__ = 'VISIT_LOG'

    log_id     = db.Column(db.Integer, primary_key=True, autoincrement=True)
    visit_date = db.Column(db.Date,    nullable=False)
    in_time    = db.Column(db.Time,    nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('STUDENT.student_id'), nullable=False)
    visitor_id = db.Column(db.Integer, db.ForeignKey('VISITOR.visitor_id'), nullable=False)

    def to_dict(self):
        return {
            'log_id':     self.log_id,
            'visit_date': self.visit_date.strftime('%Y-%m-%d'),
            'in_time':    self.in_time.strftime('%H:%M'),
            'student_id': self.student_id,
            'visitor_id': self.visitor_id
        }


# ─────────────────────────────────────────
#  HELPER: seed sample data
# ─────────────────────────────────────────

def seed_data():
    if Student.query.count() == 0:
        students = [
            Student(student_id=101, name='Anandha Ruban', room_no='A101', phone='9876543210'),
            Student(student_id=102, name='Rahul Kumar',   room_no='A102', phone='9123456780'),
            Student(student_id=103, name='Suresh Kumar',  room_no='B201', phone='9012345678'),
        ]
        db.session.add_all(students)

    if Visitor.query.count() == 0:
        visitors = [
            Visitor(visitor_id=201, name='Ravi Kumar',  phone='9988776655', relation='Father'),
            Visitor(visitor_id=202, name='Meena Devi',  phone='9877766554', relation='Mother'),
            Visitor(visitor_id=203, name='Arun',        phone='9090909090', relation='Friend'),
        ]
        db.session.add_all(visitors)

    if VisitLog.query.count() == 0:
        logs = [
            VisitLog(log_id=301, visit_date=date(2026, 2, 10), in_time=time(10, 30), student_id=101, visitor_id=201),
            VisitLog(log_id=302, visit_date=date(2026, 2, 12), in_time=time(15,  0), student_id=102, visitor_id=202),
            VisitLog(log_id=303, visit_date=date(2026, 2, 15), in_time=time(17, 45), student_id=101, visitor_id=203),
        ]
        db.session.add_all(logs)

    db.session.commit()


# ─────────────────────────────────────────
#  STUDENT ROUTES
# ─────────────────────────────────────────

@app.route('/api/students', methods=['GET'])
def get_students():
    """Retrieve all students."""
    students = Student.query.order_by(Student.student_id).all()
    return jsonify([s.to_dict() for s in students])


@app.route('/api/students/<int:student_id>', methods=['GET'])
def get_student(student_id):
    """Retrieve a single student by ID."""
    student = Student.query.get_or_404(student_id)
    return jsonify(student.to_dict())


@app.route('/api/students', methods=['POST'])
def add_student():
    """Add a new student."""
    data = request.get_json()

    # Validate required fields
    required = ['student_id', 'name', 'room_no', 'phone']
    for field in required:
        if not data.get(field):
            return jsonify({'error': f'Field "{field}" is required.'}), 400

    # Check duplicate student_id
    if Student.query.get(data['student_id']):
        return jsonify({'error': f'Student ID {data["student_id"]} already exists.'}), 409

    # Check unique phone (constraint)
    if Student.query.filter_by(phone=data['phone']).first():
        return jsonify({'error': 'Phone number must be unique.'}), 409

    student = Student(
        student_id=data['student_id'],
        name=data['name'],
        room_no=data['room_no'],
        phone=data['phone']
    )
    db.session.add(student)
    db.session.commit()
    return jsonify({'message': 'Student added successfully.', 'student': student.to_dict()}), 201


@app.route('/api/students/<int:student_id>', methods=['PUT'])
def update_student(student_id):
    """Update student record."""
    student = Student.query.get_or_404(student_id)
    data = request.get_json()

    student.name    = data.get('name',    student.name)
    student.room_no = data.get('room_no', student.room_no)
    student.phone   = data.get('phone',   student.phone)

    db.session.commit()
    return jsonify({'message': 'Student updated.', 'student': student.to_dict()})


@app.route('/api/students/<int:student_id>', methods=['DELETE'])
def delete_student(student_id):
    """Delete a student (cascades to visit logs)."""
    student = Student.query.get_or_404(student_id)
    db.session.delete(student)
    db.session.commit()
    return jsonify({'message': f'Student {student_id} deleted.'})


# ─────────────────────────────────────────
#  VISITOR ROUTES
# ─────────────────────────────────────────

@app.route('/api/visitors', methods=['GET'])
def get_visitors():
    """Retrieve all visitors."""
    visitors = Visitor.query.order_by(Visitor.visitor_id).all()
    return jsonify([v.to_dict() for v in visitors])


@app.route('/api/visitors/<int:visitor_id>', methods=['GET'])
def get_visitor(visitor_id):
    """Retrieve a single visitor by ID."""
    visitor = Visitor.query.get_or_404(visitor_id)
    return jsonify(visitor.to_dict())


@app.route('/api/visitors', methods=['POST'])
def add_visitor():
    """Add a new visitor."""
    data = request.get_json()

    required = ['visitor_id', 'name', 'phone', 'relation']
    for field in required:
        if not data.get(field):
            return jsonify({'error': f'Field "{field}" is required.'}), 400

    if Visitor.query.get(data['visitor_id']):
        return jsonify({'error': f'Visitor ID {data["visitor_id"]} already exists.'}), 409

    visitor = Visitor(
        visitor_id=data['visitor_id'],
        name=data['name'],
        phone=data['phone'],
        relation=data['relation']
    )
    db.session.add(visitor)
    db.session.commit()
    return jsonify({'message': 'Visitor added successfully.', 'visitor': visitor.to_dict()}), 201


@app.route('/api/visitors/<int:visitor_id>', methods=['DELETE'])
def delete_visitor(visitor_id):
    """Delete a visitor (cascades to visit logs)."""
    visitor = Visitor.query.get_or_404(visitor_id)
    db.session.delete(visitor)
    db.session.commit()
    return jsonify({'message': f'Visitor {visitor_id} deleted.'})


# ─────────────────────────────────────────
#  VISIT LOG ROUTES
# ─────────────────────────────────────────

@app.route('/api/visits', methods=['GET'])
def get_visits():
    """
    Retrieve all visit logs with JOINed student & visitor names.
    SQL equivalent:
        SELECT S.name, V.name, L.visit_date, L.in_time
        FROM VISIT_LOG L
        JOIN STUDENT S ON S.student_id = L.student_id
        JOIN VISITOR V ON V.visitor_id = L.visitor_id
        ORDER BY L.visit_date DESC, L.in_time DESC
    """
    logs = (
        db.session.query(VisitLog, Student, Visitor)
        .join(Student, VisitLog.student_id == Student.student_id)
        .join(Visitor, VisitLog.visitor_id == Visitor.visitor_id)
        .order_by(VisitLog.visit_date.desc(), VisitLog.in_time.desc())
        .all()
    )
    result = []
    for log, student, visitor in logs:
        result.append({
            'log_id':       log.log_id,
            'visit_date':   log.visit_date.strftime('%Y-%m-%d'),
            'in_time':      log.in_time.strftime('%H:%M'),
            'student_id':   student.student_id,
            'student_name': student.name,
            'room_no':      student.room_no,
            'visitor_id':   visitor.visitor_id,
            'visitor_name': visitor.name,
            'visitor_phone':visitor.phone,
            'relation':     visitor.relation
        })
    return jsonify(result)


@app.route('/api/visits', methods=['POST'])
def add_visit():
    """Log a new visit. Auto-generates log_id."""
    data = request.get_json()

    required = ['student_id', 'visitor_id', 'visit_date', 'in_time']
    for field in required:
        if not data.get(field):
            return jsonify({'error': f'Field "{field}" is required.'}), 400

    # Validate FK existence
    if not Student.query.get(data['student_id']):
        return jsonify({'error': f'Student ID {data["student_id"]} not found.'}), 404
    if not Visitor.query.get(data['visitor_id']):
        return jsonify({'error': f'Visitor ID {data["visitor_id"]} not found.'}), 404

    try:
        visit_date = datetime.strptime(data['visit_date'], '%Y-%m-%d').date()
        in_time    = datetime.strptime(data['in_time'],    '%H:%M').time()
    except ValueError as e:
        return jsonify({'error': f'Invalid date/time format: {e}'}), 400

    log = VisitLog(
        visit_date=visit_date,
        in_time=in_time,
        student_id=data['student_id'],
        visitor_id=data['visitor_id']
    )
    db.session.add(log)
    db.session.commit()
    return jsonify({'message': 'Visit logged successfully.', 'log': log.to_dict()}), 201


@app.route('/api/visits/<int:log_id>', methods=['DELETE'])
def delete_visit(log_id):
    """Delete a visit log entry."""
    log = VisitLog.query.get_or_404(log_id)
    db.session.delete(log)
    db.session.commit()
    return jsonify({'message': f'Visit log {log_id} deleted.'})


# ─────────────────────────────────────────
#  STATISTICS / DASHBOARD ROUTE
# ─────────────────────────────────────────

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """
    Dashboard statistics using aggregate functions:
    - COUNT of students, visitors, total visits
    - Latest visit date (MAX)
    - Most visited student
    """
    from sqlalchemy import func

    total_students = Student.query.count()
    total_visitors = Visitor.query.count()
    total_visits   = VisitLog.query.count()

    # MAX(visit_date)
    latest = db.session.query(func.max(VisitLog.visit_date)).scalar()

    # Most visited student (GROUP BY + ORDER BY + LIMIT)
    top = (
        db.session.query(Student.name, func.count(VisitLog.log_id).label('cnt'))
        .join(VisitLog, Student.student_id == VisitLog.student_id)
        .group_by(Student.student_id)
        .order_by(func.count(VisitLog.log_id).desc())
        .first()
    )

    return jsonify({
        'total_students': total_students,
        'total_visitors': total_visitors,
        'total_visits':   total_visits,
        'latest_visit':   latest.strftime('%Y-%m-%d') if latest else None,
        'top_student':    top[0] if top else None,
        'top_visit_count':top[1] if top else 0
    })


# ─────────────────────────────────────────
#  SEARCH ROUTE
# ─────────────────────────────────────────

@app.route('/api/search', methods=['GET'])
def search():
    """
    Search visit logs by student name or visitor name.
    Uses LIKE queries (subquery pattern).
    """
    q = request.args.get('q', '').strip()
    if not q:
        return jsonify([])

    pattern = f'%{q}%'

    logs = (
        db.session.query(VisitLog, Student, Visitor)
        .join(Student, VisitLog.student_id == Student.student_id)
        .join(Visitor, VisitLog.visitor_id == Visitor.visitor_id)
        .filter(
            db.or_(
                Student.name.ilike(pattern),
                Visitor.name.ilike(pattern),
                Student.room_no.ilike(pattern)
            )
        )
        .order_by(VisitLog.visit_date.desc())
        .all()
    )

    result = []
    for log, student, visitor in logs:
        result.append({
            'log_id':       log.log_id,
            'visit_date':   log.visit_date.strftime('%Y-%m-%d'),
            'in_time':      log.in_time.strftime('%H:%M'),
            'student_name': student.name,
            'room_no':      student.room_no,
            'visitor_name': visitor.name,
            'visitor_phone':visitor.phone,
            'relation':     visitor.relation
        })
    return jsonify(result)


# ─────────────────────────────────────────
#  HEALTH CHECK
# ─────────────────────────────────────────

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'message': 'Hostel Visitor Log System Backend Running'})


# ─────────────────────────────────────────
#  APP ENTRY POINT
# ─────────────────────────────────────────

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_data()
        print("✅ Database initialized with sample data.")
    app.run(debug=True, host='0.0.0.0', port=5000)
