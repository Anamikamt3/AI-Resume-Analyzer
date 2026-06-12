# AI Resume Analyzer & Job Matcher (ATS Engine)

A complete web application ecosystem built with Django REST Framework, PostgreSQL, and the Groq Llama-3.3 Cloud inference engine. This platform securely parses uploaded candidate resumes (.pdf), extracts localized skill sets, and cross-evaluates candidate profiles against target job requirements to generate a quantitative alignment score and actionable gap-analysis feedback.

---

## 🚀 Key Features

* User Authentication Management: Guarded session lifecycles using JSON Web Tokens (JWT via SimpleJWT).
* Document Extraction Interface: Asynchronous parsing workflows supporting .pdf file text isolation via PyPDF.
* Intelligent Analysis Layer: Deterministic text evaluation mapping executed via Llama-3.3-70b-versatile running at 0.2 temperature.
* Continuous Integration: Automated system validation matrix utilizing GitHub Actions pipelines.

---

## 🛠️ System Architecture & Tech Stack

* Backend Engine: Django, Django REST Framework (DRF)
* Database Layer: PostgreSQL Database cluster
* Core AI Integration: Groq Cloud Inference SDK (Llama 3.3 Engine)
* Production Web Gateway: Gunicorn
* Automation Tooling: GitHub Actions CI Matrix
* Swagger : API Documentation





