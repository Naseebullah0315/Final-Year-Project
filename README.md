📚 Learning Management System (LMS)
📖 Project Overview
The Learning Management System (LMS) is a Django-based web application developed as a Final Year Project.
It provides a digital platform to manage university-related academic and administrative activities, including student management, teacher management, attendance tracking, and marks management.
This project aims to simplify educational workflows by offering dedicated portals for Students, Teachers, HODs (Heads of Departments), and Admins.
________________________________________
🚀 Features
🔹 Admin Portal
•	Manage departments, semesters, and courses.
•	Add, update, or remove teachers and students.
•	Assign roles (Teacher / HOD).
•	View overall statistics (students, teachers, courses).
🔹 Teacher Portal
•	Mark attendance for assigned classes.
•	Upload and manage marks (Assignments, Quizzes, Midterm, Final, etc.).
•	View student performance reports.
🔹 HOD Portal
•	Dual role: HOD + Teacher (toggle without logout).
•	Approve/manage teachers under the department.
•	Monitor departmental performance.
🔹 Student Portal
•	View profile and enrolled courses.
•	Check attendance records.
•	View marks (Assignments, Quizzes, Midterm, Final).
•	Download academic reports.
________________________________________
🛠️ Technology Stack
•	Backend: Django (Python)
•	Frontend: HTML, CSS, Bootstrap, JavaScript
•	Database: SQLite (default, can be upgraded to MySQL/PostgreSQL)
•	Authentication: Django’s built-in authentication system
•	Other Tools: Git/GitHub for version control
________________________________________
⚙️ Installation & Setup
Prerequisites
Make sure you have installed:
•	Python 3.x
•	pip (Python package manager)
•	Virtual environment (optional but recommended)

Steps

# Clone the repository
git clone https://github.com/Naseebullah0315/Final-Year-Project.git

# Navigate into the project folder
cd Final-Year-Project

# Create virtual environment
python -m venv venv
source venv/bin/activate    # On Linux/Mac
venv\Scripts\activate       # On Windows

# Install dependencies
pip install -r requirements.txt

# Run database migrations
python manage.py migrate

# Create superuser (Admin account)
python manage.py createsuperuser

# Run the development server
python manage.py runserver


Now visit: http://127.0.0.1:8000/
in your browser.

📂 Project Structure
Final-Year-Project/
│── lms/                # Main Django project settings
│── accounts/           # User authentication & profiles
│── students/           # Student portal logic
│── teachers/           # Teacher portal logic
│── hod/                # HOD (Head of Department) portal
│── admin_panel/        # Admin functionalities
│── templates/          # HTML templates
│── static/             # CSS, JS, images
│── db.sqlite3          # Database (SQLite default)
│── manage.py           # Django management script


🧑💻 Usage
•	Admin logs in → adds departments, teachers, students.
•	Teacher logs in → marks attendance, uploads marks.
•	HOD logs in → manages department + can toggle to teacher role.
•	Student logs in → views attendance, marks, and reports.
________________________________________
🔮 Future Enhancements
•	Integration with Google Classroom / Zoom.
•	Advanced analytics & reporting.
•	Mobile app version using Flutter / React Native.
•	Real-time notifications for students & teachers.
________________________________________
🤝 Contribution
This project was developed as part of a Final Year Project.
Contributions, suggestions, and improvements are always welcome!
________________________________________
📜 License
This project is for academic purposes only.
Feel free to use and modify it for learning and research.
________________________________________


✨ Developed by: Naseebullah


