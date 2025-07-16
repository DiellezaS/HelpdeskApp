# Helpdesk System

A full-featured Django-based Helpdesk application for managing IT support tickets, with role-based dashboards and interactive ticket workflows.

---

## Table of Contents

- [Project Overview](#project-overview)  
- [Features](#features)  
- [Installation](#installation)
- [Environment Setup & Database](#environment-setup--database) 
- [Usage](#usage)  
- [Project Structure](#project-structure)  
- [Technologies](#technologies)  
- [Future Enhancements](#future-enhancements)  
- [License](#license)  
- [Contact](#contact)  

---

## Project Overview

This Helpdesk Ticketing System allows users to create, track, and manage IT support tickets. The system supports multiple roles:

- **Admins:**
- The **first user created** during setup is assigned the **Admin** role automatically.  
- Only Admins can add new users and assign roles (Worker or Agent).  
- Admins have full control over user management and oversee the entire helpdesk operation, including permissions and user roles.  
- Admins can manage all tickets and system settings through the admin interface.

- **Agents:** View, claim, update, and resolve tickets; access detailed dashboards with charts and recent activity.  
- **Workers:** Create tickets, comment, and track status via a personal dashboard.
- 
The application includes advanced filtering, status updates, comments, notifications of recent activities, and interactive data visualization.

---

## Features

### Authentication & Roles
- User login/logout with role-based access (Agent, Worker, Admin).  
- Separate dashboards and views per role.

### Ticket Management
- Create, view, update, and comment on tickets.  
- Ticket statuses: Open, In Progress, Resolved, Closed.  
- Ticket priorities: High, Medium, Low.  
- Ticket categories: Software, Hardware, Network, Other.  
- Assign or claim tickets (unassigned tickets view).

### Dashboards
- Agent dashboard with interactive charts:  
  - Pie chart showing ticket status breakdown.  
  - Bar chart for tickets by priority.  
  - Line chart for ticket trends over time.  
- Filtering and searching tickets with date ranges and multiple criteria.  
- Recent activity modal showing latest events (comments, status changes).

### Worker Dashboard
- Access a built-in **FAQ chatbot** to get quick answers to common questions and potentially resolve issues without creating a ticket.  
- If the FAQ chatbot does not resolve the issue, users can then create a new support ticket.  
- View personal tickets, comment on them, and track their progress.  
- Easy navigation between FAQ, ticket lists, and ticket creation.
- 
### UI/UX
- Responsive design with Google Fonts (Quicksand).  
- Consistent styling using CSS and Bootstrap.  
- Modal dialogs and AJAX for dynamic content loading.

### Charts
- Interactive charts built with Chart.js to visualize ticket data.
- Ticket Status Pie Chart: Displays distribution of tickets by status (Open, In Progress, Resolved, Closed).
- Priority Bar Chart: Shows number of tickets per priority level (High, Medium, Low).
- Trend Line Chart: Visualizes tickets accepted over time, enabling tracking of ticket volume trends.
- Charts support clickable elements to filter tickets by status, priority, or date directly from the dashboard.
- Responsive and accessible chart designs for easy data interpretation.

---

## Installation

1. **Clone the repo:**

   ```bash
   git clone https://github.com/DiellezaS/HelpdeskApp.git
   cd helpdeskApp

2. **Create a new conda environment:**
   ```bash
   conda create --name myenv python=3.11
   ```

3. **Activate the environment:**
   ```bash
   conda activate myenv
   ```

4. **Install dependencies:**
 
   ```bash
   conda install django
   conda install -c conda-forge chartjs
   ```
  ```bash
   pip install -r requirements.txt
   ```
5. **Run migrations:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create the admin user (first user):**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the server:**
   ```bash
   python manage.py runserver
   ```

---

### Environment Setup & Database
Before running the project or the batch script, activate your Conda environment:
conda activate myenv
The project uses SQLite3 by default, so no extra database setup is required.

The SQLite database file (db.sqlite3) will be created automatically after migrations.

To reset the database, simply delete db.sqlite3 and rerun migrations:
rm db.sqlite3
python manage.py migrate


## Usage

- Log in according to your role (Admin, Agent, Worker).  
- Admins manage users and system settings.  
- Agents handle ticket processing and resolution.  
- Workers create and track their tickets, use the FAQ chatbot for support.

---

## Project Structure

- `helpdesk/` - Django project folder.  
- `tickets/` - Main app handling ticket creation, views, models, forms.  
- `templates/` - HTML templates for different roles and pages.  
- `static/` - CSS, JavaScript.
- `manage.py` - Django management script.

---

## Technologies

- Python 3.11
- Django  
- Anaconda (for environment management)  
- Chart.js (for charts)  
- Bootstrap and CSS for styling  
- JavaScript and AJAX for interactivity

---

## Deployment with ngrok (Local Development and Testing)

In this project, I have used **ngrok** to expose the local Django development server to the internet. This allows easy external access for demos, testing, or remote collaboration without the need for a full production deployment.

### Prerequisites
- Download and install ngrok from [https://ngrok.com/download](https://ngrok.com/download).

### How I set it up

To streamline the process, I created a batch file `run_django_ngrok.bat` that:

- Activates the Anaconda environment.  
- Starts the Django development server.  
- Opens an ngrok tunnel on port 8000.

### run_django_ngrok.bat (Windows)

```bat
@echo off
:: Anaconda base path
set CONDA_PATH=C:\Users\USER\anaconda3

:: Environment name
set ENV_NAME=myenv

:: Project directory
set PROJECT_PATH=C:\Users\USER\OneDrive\Desktop\Helpdesk

:: Ngrok full path
set NGROK_PATH=C:\Users\USER\AppData\Local\Programs\ngrok.exe

:: Start Django server in new window
start "Anaconda Django Server" cmd /k "%CONDA_PATH%\condabin\conda.bat activate %ENV_NAME% && cd /d %PROJECT_PATH% && python manage.py runserver"

:: Wait 5 seconds to ensure Django starts
timeout /t 5 >nul

:: Start ngrok using full path
start "Anaconda ngrok" cmd /k "%CONDA_PATH%\condabin\conda.bat activate %ENV_NAME% && cd /d %PROJECT_PATH% && %NGROK_PATH% http 8000"

```
## License
This project is licensed under the MIT License.

## Contact
Created by Dielleza S.
GitHub: https://github.com/DiellezaS

