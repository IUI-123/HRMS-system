# Sangi RCM - HRMS Portal

A company HR Management System built with Django.

## Requirements
- Python 3.11+
- cmake (for face recognition)
- brew (Mac package manager)

## Setup Instructions

### 1. Clone the repository
git clone https://github.com/IUI-123/HRMS-system.git
cd HRMS-system

### 2. Install Python 3.11
brew install python@3.11

### 3. Create and activate virtual environment
/opt/homebrew/bin/python3.11 -m venv venv
source venv/bin/activate

### 4. Install system dependencies
brew install cmake cairo pkg-config

### 5. Install Python dependencies
cd sangi_rcm
pip install -r requirements.txt

### 6. Run migrations
python manage.py migrate

### 7. Create superuser
python manage.py createsuperuser

### 8. Run the server
python manage.py runserver

Open http://127.0.0.1:8000/ in your browser.

## To run the project every time
cd HRMS-system
source venv/bin/activate
cd sangi_rcm
python manage.py runserver
