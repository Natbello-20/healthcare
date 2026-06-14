# Hospital Appointment System

A comprehensive hospital management platform built with Python and Flask. This application handles role-based workflows for Administrators, Doctors, and Patients, ensuring secure access and preventing appointment conflicts.

## Features

- **Role-Based Access Control**: Separate dashboards for Admin, Doctor, and Patient.
- **Appointment Conflict Prevention**: Validates doctor availability before confirming a booking.
- **Admin Management**: Create departments, register doctors, and view system-wide logs.
- **Doctor Workflow**: View daily schedules, update appointment status (Completed, No Show), and leave consultation notes.
- **Patient Portal**: Easy registration, self-service booking, and historical appointment tracking.
- **Responsive Design**: Styled with Bootstrap for use across desktop and mobile devices.

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

## Installation

1. Clone or download this project.
2. Open your terminal in the project directory.
3. Install the required dependencies:
    pip install -r requirements.txt
cl
## Running the Application

1. Start the Flask server:
    python app.py
2. Open your web browser and navigate to:
    http://127.0.0.1:5000

## Initial Configuration

The application automatically initializes a SQLite database (`hospital.db`) and a default Administrator account on first run.

- **Admin Login**:
  - Username: `admin`
  - Password: `admin123`

### Suggested Setup Flow
1. Login as **Admin**.
2. Create at least one **Department** (e.g., git add requirements.txt
git commit -m "Add requirements file for deployment"
git push origin main).
3. Register a **Doctor** and assign them to a department.
4. Logout and use the **Patient Registration** on the homepage to create a patient account.
5. Log in as a **Patient** to book your first appointment.

## Project Structure

- `app.py`: Main application logic, routing, and business logic.
- `models.py`: Database schema definitions using SQLAlchemy.
- `templates/`: HTML templates using Jinja2 engine.
- `requirements.txt`: Project dependencies.

## Troubleshooting

- **Database Errors**: If the database schema changes, delete `hospital.db` and restart the application to regenerate it.
- **Port Conflict**: If port 5000 is in use, you can change the port in `app.py` by modifying `app.run(port=XXXX)`.
