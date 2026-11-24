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
## Attendance Management

Teachers can use AttendEase to record and manage student attendance.

- Select the relevant academic subject.
- View the registered students.
- Mark attendance for students.
- Save attendance records for tracking.
- Review attendance information through the dashboard and reports.
## Attendance Reports

AttendEase helps users monitor attendance records and review attendance-related information.

- View recorded attendance data.
- Track attendance by academic subject.
- Review student attendance records.
- Use dashboard summaries to monitor attendance.
## Dashboard Overview

The AttendEase dashboard provides a central interface for accessing attendance-related functions.

- Displays attendance-related summaries.
- Provides navigation to system features.
- Offers access to student and teacher functionality.
- Organizes attendance information for convenient access.
## Dashboard Overview

The AttendEase dashboard provides a central interface for accessing attendance-related functions.

- Displays attendance-related summaries.
- Provides navigation to system features.
- Offers access to student and teacher functionality.
- Organizes attendance information for convenient access.
## Benefits of AttendEase

AttendEase simplifies attendance management through a digital platform.

- Reduces manual attendance record-keeping.
- Makes attendance information easier to access.
- Organizes records by student and academic subject.
- Helps teachers manage attendance efficiently.
- Allows students to review their attendance records.
## Security Considerations

AttendEase uses role-based access to organize system functionality for teachers and students.

- Users access features according to their assigned role.
- Attendance records are stored in the application's database.
- Login access helps protect attendance functionality.
- Users should keep their login credentials confidential.
## Technology Stack

AttendEase is built using the following technologies:

- **Python:** Application programming language.
- **Flask:** Web framework for handling application routes and requests.
- **SQLite:** Database for storing attendance-related information.
- **HTML:** Structure of application web pages.
- **CSS:** Styling and layout of the user interface.