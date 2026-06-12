AI RESUME ANALYZER & JOB MATCHER — REST API DOCUMENTATION


This documentation details the available API routing endpoints, payload schemas, 
and token-handling structures for the AI Resume Analyzer application stack.

All endpoints return standardized JSON payloads. Protected resources require a
valid JSON Web Token (JWT) sent via the HTTP Authorization header.

--------------------------------------------------------------------------------
1. AUTHENTICATION & SESSION ENDPOINTS
--------------------------------------------------------------------------------

### REGISTER USER PROFILE
* URL:        /api/auth/register/
* Method:     POST
* Access:     Public
* Format:     application/json

Request Body:
{
  "username": "candidate_clara",
  "email": "clara.dev@example.com",
  "password": "SecurePassword123!"
}

Response (201 Created):
{
  "message": "User registered successfully.",
  "user": {
    "username": "candidate_clara",
    "email": "clara.dev@example.com"
  }
}

---

### OBTAIN JWT ACCESS PAIR (LOGIN)
* URL:        /api/token/
* Method:     POST
* Access:     Public
* Format:     application/json

Request Body:
{
  "username": "candidate_clara",
  "password": "SecurePassword123!"
}

Response (200 OK):
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...[Encrypted Hash]",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...[Encrypted Hash]"
}

---

### REFRESH ACCESS TOKEN
* URL:        /api/token/refresh/
* Method:     POST
* Access:     Public
* Format:     application/json

Request Body:
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...[Encrypted Hash]"
}

Response (200 OK):
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...[Fresh Access Hash]"
}


--------------------------------------------------------------------------------
2. CORE AI & ANALYSIS ENDPOINTS
--------------------------------------------------------------------------------
* Require Header: Authorization: Bearer <your_access_token>

### ANALYZE RESUME COMPATIBILITY FIT
* URL:        /api/analyze/
* Method:     POST
* Access:     Authenticated (JWT)
* Format:     multipart/form-data

Request Parameters:
- "resume":          File binary object (.pdf or .docx format)
- "job_description": Plain text string block detailing target job criteria

Response (200 OK):
{
  "match_score": 82,
  "skills": ["Python", "Django", "PostgreSQL", "REST APIs", "Tailwind CSS"],
  "feedback": {
    "strengths": [
      "Robust backend engineering architecture using Django REST framework.",
      "Clean implementation of JWT-secured session handlers."
    ],
    "gaps": [
      "No explicit evidence of Docker containerization strategies found.",
      "Lacks direct mention of Cloud Native deployment pipelines (AWS/GCP)."
    ],
    "skills": ["Python", "Django", "PostgreSQL", "REST APIs", "Tailwind CSS"]
  },
  "filename": "Clara_Backend_Engineer.pdf",
  "analyzed_at": "2026-06-12 14:15:22"
}

HTTP Status Codes:
- 200 OK:          Processing succeeded; analysis completed cleanly.
- 400 Bad Request: Missing input parameters or unsupported file extension.
- 401 Unauthorized: Missing, invalid, or expired JWT access token header.
- 502 Bad Gateway: LLM inference provider returned an unparseable response structure.

---

### FETCH PERSONAL ANALYSIS LEDGER HISTORY
* URL:        /api/history/
* Method:     GET
* Access:     Authenticated (JWT)
* Format:     application/json

Response (200 OK):
[
  {
    "id": 14,
    "filename": "Clara_Backend_Engineer.pdf",
    "analyzed_at": "2026-06-12 14:15:22",
    "match_score": 82,
    "feedback": {
      "strengths": ["Robust backend engineering architecture using Django."],
      "gaps": ["No explicit evidence of Docker containerization strategies found."],
      "skills": ["Python", "Django", "PostgreSQL", "REST APIs"]
    }
  },
  {
    "id": 8,
    "filename": "Old_Draft_Resume.docx",
    "analyzed_at": "2026-06-09 10:04:11",
    "match_score": 45,
    "feedback": {
      "strengths": ["Basic foundational markdown structure exists."],
      "gaps": ["Missing structural enterprise database integration experience."],
      "skills": ["HTML", "CSS"]
    }
  }
]

HTTP Status Codes:
- 200 OK:          History retrieved successfully (returns empty array [] if clean).
- 401 Unauthorized: Authorization token verification failed.
