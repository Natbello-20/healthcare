import os
from flask import Flask, render_template, redirect, url_for, request, flash, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from models import db, User, Patient, Doctor, Department, Appointment

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hospital-mgmt-secret-key-12345'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hospital.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- Initialization ---
@app.before_request
def create_tables():
    # Only create if they don't exist
    if not os.path.exists('hospital.db'):
        with app.app_context():
            db.create_all()
            # Create a default admin if not exists
            if not User.query.filter_by(username='admin').first():
                admin = User(
                    username='admin', 
                    password=generate_password_hash('admin123'), 
                    role='admin'
                )
                db.session.add(admin)
                db.session.commit()

# --- Auth Routes ---
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid username or password', 'danger')
    return render_template('login.html')

@app.route('/register_patient', methods=['GET', 'POST'])
def register_patient():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        name = request.form.get('name')
        phone = request.form.get('phone')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return redirect(url_for('register_patient'))
        
        new_user = User(username=username, password=generate_password_hash(password), role='patient')
        db.session.add(new_user)
        db.session.flush() # Get ID
        
        new_patient = Patient(user_id=new_user.id, name=name, phone=phone)
        db.session.add(new_patient)
        db.session.commit()
        
        flash('Account created! Please login.', 'success')
        return redirect(url_for('login'))
    return render_template('register_patient.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'admin':
        return render_template('admin_dashboard.html', 
                               depts=Department.query.all(),
                               doctors=Doctor.query.all(),
                               appts=Appointment.query.order_by(Appointment.date.desc()).all())
    elif current_user.role == 'doctor':
        doctor = current_user.doctor_profile
        appts = Appointment.query.filter_by(doctor_id=doctor.id).order_by(Appointment.date.desc(), Appointment.time.desc()).all()
        return render_template('doctor_dashboard.html', doctor=doctor, appointments=appts)
    else:
        patient = current_user.patient_profile
        appts = Appointment.query.filter_by(patient_id=patient.id).order_by(Appointment.date.desc()).all()
        return render_template('patient_dashboard.html', patient=patient, appointments=appts)

# --- Admin Routes ---
@app.route('/admin/add_dept', methods=['POST'])
@login_required
def add_dept():
    if current_user.role != 'admin': abort(403)
    name = request.form.get('name')
    if name:
        new_dept = Department(name=name)
        db.session.add(new_dept)
        db.session.commit()
        flash(f'Department {name} added.', 'success')
    return redirect(url_for('dashboard'))

@app.route('/admin/add_doctor', methods=['POST'])
@login_required
def add_doctor():
    if current_user.role != 'admin': abort(403)
    username = request.form.get('username')
    password = request.form.get('password')
    name = request.form.get('name')
    spec = request.form.get('specialization')
    dept_id = request.form.get('department_id')
    
    if User.query.filter_by(username=username).first():
        flash('Username exists', 'danger')
    else:
        u = User(username=username, password=generate_password_hash(password), role='doctor')
        db.session.add(u)
        db.session.flush()
        d = Doctor(user_id=u.id, name=name, specialization=spec, department_id=dept_id)
        db.session.add(d)
        db.session.commit()
        flash(f'Doctor {name} registered.', 'success')
    return redirect(url_for('dashboard'))

# --- Patient Routes ---
@app.route('/book_appointment', methods=['GET', 'POST'])
@login_required
def book_appointment():
    if current_user.role != 'patient':
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        doctor_id = request.form.get('doctor_id')
        date_str = request.form.get('date')
        time_str = request.form.get('time')
        
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        time_obj = datetime.strptime(time_str, '%H:%M').time()
        
        # Conflict Check
        exists = Appointment.query.filter_by(
            doctor_id=doctor_id, 
            date=date_obj, 
            time=time_obj
        ).first()
        
        if exists:
            flash('This doctor is already booked at this specific time. Please choose another slot.', 'danger')
        else:
            new_appt = Appointment(
                patient_id=current_user.patient_profile.id,
                doctor_id=doctor_id,
                date=date_obj,
                time=time_obj
            )
            db.session.add(new_appt)
            db.session.commit()
            flash('Appointment booked successfully!', 'success')
            return redirect(url_for('dashboard'))
            
    doctors = Doctor.query.all()
    return render_template('book_appointment.html', doctors=doctors)

# --- Doctor Routes ---
@app.route('/update_appointment/<int:id>', methods=['POST'])
@login_required
def update_appointment(id):
    if current_user.role != 'doctor':
        abort(403)
        
    appt = Appointment.query.get_or_404(id)
    if appt.doctor_id != current_user.doctor_profile.id:
        abort(403)
        
    appt.status = request.form.get('status')
    appt.notes = request.form.get('notes')
    db.session.commit()
    flash('Appointment updated.', 'info')
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)
