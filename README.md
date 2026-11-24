# AttendEase – Attendance Management System

AttendEase is a web-based attendance management system developed using Python, Flask, SQLite, HTML and CSS.

## Features
- Teacher login and dashboard
- Student management
- Subject-wise attendance marking
- Attendance records
- Reports and analytics
- Student personal dashboard
- Attendance calendar
- Profile management
- Settings

## Technologies Used
- Python
- Flask
- SQLite
- HTML
- CSS
## System Roles

### Teacher
- Manage student records
- Mark and update attendance
- View subject-wise attendance
- Access attendance reports and analytics

### Student
- View personal attendance records
- Check attendance percentages
- View attendance subject-wise
- Track attendance history
## Project Structure

- app.py — Main Flask application
- templates/ — HTML pages for the application
- static/ — CSS styles and static assets
- requirements.txt — Project dependencies
- README.md — Project documentation
## Git Ignore

The project excludes virtual environments, Python cache files, local database files and system-generated files from version control to keep the repository clean.
## Installation and Setup

1. Clone the repository
2. Create a Python virtual environment
3. Install dependencies using pip
4. Run the Flask application

### Commands

- python3 -m venv venv
- source venv/bin/activate
- pip install -r requirements.txt
- python3 app.py
## Core Modules

- Student Management
- Attendance Marking
- Attendance Records
- Subject Management
- Attendance Analytics
- Student Dashboard
- Teacher Dashboard
## Subjects Supported

- Signal Transformation
- Data Science and Analytics
- Machine Learning and Pattern Recognition
- Version Control Using GitHub
- Environment and Sustainability
- Advanced Data Structures and Algorithms
- Mathematics for Computing
- Programming for Artificial Intelligence
## Login System

AttendEase provides role-based access for users:

- **Teacher/Admin:** Access the dashboard, manage students and subjects, mark attendance, and view attendance reports.
- **Student:** Access the student dashboard and view personal attendance records.

Users access the system through the login page, which directs them to the dashboard corresponding to their role.