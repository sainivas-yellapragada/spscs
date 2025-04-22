# 🚀 SPSCS – *Software Progress Status Checking System*

**Track Progress. Empower Teams. Deliver Excellence.**

---

## 🌟 Overview

**SPSCS** is a full-stack project management and progress tracking system built to simplify how teams handle software projects. From **task assignments** to **collaborative updates**, it brings structure and visibility to your workflow. Perfect for developers, project leads, and academic teams!

---

## 🔑 Core Features

### 🔐 Authentication & Access Control
- Google OAuth login  
- Github login  
- Traditional email/password via Django Allauth  
- Role-based access: Admin,Team Member or employee  

### 🤩 Project Management
- Create, edit, and delete projects  
- Assign team members with defined roles  
- Set milestones and project deadlines  

### ✅ Task Management
- Create and assign tasks  
- Priority levels and status updates (To Do, In Progress, Completed)  
- Track task history and updates  

### 💬 Collaboration
- Excalidraw for Whiteboard required tasks such as brainstorming
- In-app notifications for updates and deadlines  

### 📈 Dashboard & Reports
- Visual summary of ongoing projects  
- Task completion and productivity stats  
- User activity insights  

### ↺ Tech Migration
- Smooth migration from **MySQL** to **PostgreSQL** and vice versa 

---

## 🛠️ Tech Stack

- **Backend**: Django, Django REST Framework  
- **Frontend**: HTML, CSS, JavaScript 
- **Database**: MySQl (Development) and PostgreSQL (Production)  
- **Authentication**: Django Allauth (OAuth + traditional)

---

## ⚙️ Installation & Setup

```bash
# Clone the repo
git clone https://github.com/sainivas-yellapragada/pms.git
cd pms

# Create a virtual environment
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment (.env) file with DB and OAuth credentials

# Run database migrations
python manage.py migrate

# Start the development server
python manage.py runserver
```

---

## 🚀 Getting Started

1. Sign up using Google, LinkedIn, or email/password.  
2. Create a new project and invite team members.  
3. Add tasks, assign them, and track progress.  
4. Collaborate via comments and view real-time updates.  
5. Monitor progress with visual dashboards.
6. Schedule, manage metings

---

## 🔮 Coming Soon

- 📌 File attachments within tasks  
- 📧 Email notifications  
- 📱 Fully responsive mobile UI

