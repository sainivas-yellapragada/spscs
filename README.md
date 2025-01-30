
# Project Title

A brief description of what this project does and who it's for

Project Management System (PMS) - Overview
1. Project Name:
Project Management System (PMS)

2. Description:
PMS is a full-stack project management web application built using Django and MongoDB. It allows users to manage projects, track tasks, collaborate with team members, and monitor progress efficiently. The system supports multiple authentication methods, including Google OAuth, LinkedIn login, and traditional email/password registration.

3. Features:
User Authentication & Authorization:
Google OAuth login
LinkedIn login
Traditional email/password authentication using Django Allauth
User Roles & Permissions:
Admin, Manager, Team Member roles
Project Management:
Create, update, and delete projects
Assign users to projects
Define project deadlines and milestones
Task Management:
Create, assign, and track tasks
Set task priority levels
Status updates (To Do, In Progress, Completed)
Collaboration & Communication:
Commenting on tasks
Notifications and alerts
Dashboard & Reporting:
Overview of ongoing projects
Task completion statistics
User activity tracking
Database Migration:
Migrated from MySQL to MongoDB Compass
4. Tech Stack:
Backend: Django, Django REST Framework
Frontend: HTML, CSS, JavaScript (Optional: React or Vue for enhanced UI)
Database: MongoDB (using Django with MongoEngine)
Authentication: Django Allauth (Google & LinkedIn OAuth, traditional login)
5. Installation & Setup:
git clone https://github.com/yourusername/pms.git
cd pms

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure .env file (set database credentials and OAuth keys)

# Run migrations
python manage.py migrate

# Start the development server
python manage.py runserver

6. Usage:
Sign up or log in using Google, LinkedIn, or email/password.
Create a new project and invite team members.
Add and assign tasks within a project.
Update task progress and collaborate using comments.
View project statistics in the dashboard.
7. Future Enhancements:
Kanban board for visual task tracking
File attachments in tasks
Email notifications
Mobile-friendly UI
