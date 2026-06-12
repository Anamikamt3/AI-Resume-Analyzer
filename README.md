# AI Resume Analyzer & Job Matcher (ATS Engine)

A complete web application ecosystem built with Django REST Framework, PostgreSQL, and the Groq Llama-3.3 Cloud inference engine. This platform securely parses uploaded candidate resumes (.pdf), extracts localized skill sets, and cross-evaluates candidate profiles against target job requirements to generate a quantitative alignment score and actionable gap-analysis feedback.

---

## 🚀 Key Features

* User Authentication Management: Guarded session lifecycles using JSON Web Tokens (JWT via SimpleJWT).
* Document Extraction Interface: Asynchronous parsing workflows supporting .pdf file text isolation via PyPDF.
* Intelligent Analysis Layer: Deterministic text evaluation mapping executed via Llama-3.3-70b-versatile running at 0.2 temperature.
* Historical Audit Ledger: Relational profile mapping tracking past scans on a persistent PostgreSQL instance.
* Continuous Integration: Automated system validation matrix utilizing GitHub Actions pipelines.

---

## 🛠️ System Architecture & Tech Stack

* Backend Engine: Django, Django REST Framework (DRF)
* Database Layer: PostgreSQL Database cluster
* Core AI Integration: Groq Cloud Inference SDK (Llama 3.3 Engine)
* Production Web Gateway: Gunicorn
* Automation Tooling: GitHub Actions CI Matrix

---

## ⚙️ Local Installation & Environment Setup

Follow these steps to spin up and run the codebase workspace locally:

### 1. Clone the Code Repository Workspace
git clone https://github.com/Anamikamt3/AI-Resume-Analyzer.git
cd AI-Resume-Analyzer

### 2. Configure Your Isolated Python Virtual Environment
python -m venv venv
# On Windows PowerShell:
.\venv\Scripts\Activate.ps1
# On Linux/macOS:
source venv/bin/activate

### 3. Install Package Dependencies Matrix
pip install -r requirements.txt

### 4. Setup Local Environment Variables
Create a file named `.env` in the root repository directory and configure your private parameter keys:
SECRET_KEY=your_django_secret_key_here
GROQ_API_KEY=your_live_groq_api_credential_token_here
DATABASE_URL=your_postgresql_database_connection_string

### 5. Execute Relational Migrations
python manage.py makemigrations
python manage.py migrate

### 6. Launch the Local Development Server
python manage.py runserver

The application endpoints layer will initialize live at: http://127.0.0.1:8000/

---

## 🧪 Continuous Integration Verification

This workspace includes an automated GitHub Actions continuous integration pipeline located under `.github/workflows/django.yml`. Every code push triggers an isolated cloud container instance that builds the codebase environment from scratch, installs all listed dependency requirements, and executes a system integrity check routine (`python manage.py check`) to guarantee build stability before deployments.



