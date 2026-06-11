import os
import json
import logging
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import transaction 
from zoneinfo import ZoneInfo 
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from pypdf import PdfReader
from groq import Groq
from .models import Resume, JobAnalysis

logger = logging.getLogger(__name__)

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')

        if not username or not password or not email:
            return Response(
                {"error": "Please provide username, email, and password."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if User.objects.filter(username=username).exists():
            return Response(
                {"error": "Username already exists."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.create_user(username=username, email=email, password=password)
            return Response(
                {"message": "User registered successfully!"},
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {"error": f"Failed to create account: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ResumeAnalyzeView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsAuthenticated]

    def post(self, request):
        resume_file = request.FILES.get('resume')
        job_description = request.data.get('job_description', '').strip()

        if not resume_file:
            return Response(
                {"error": "Please upload a valid PDF resume file."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        if not job_description:
            return Response(
                {"error": "Please provide a job description to match against."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        

        resume_text = ""
        filename = resume_file.name.lower()

        try:
            if filename.endswith('.pdf'):
                # Handle PDF extraction
                from pypdf import PdfReader
                reader = PdfReader(resume_file)
                for page in reader.pages:
                    text_content = page.extract_text()
                    if text_content:
                        resume_text += text_content + "\n"

            elif filename.endswith('.docx') or filename.endswith('.doc'):
                # Handle Microsoft Word extraction
                from docx import Document
                doc = Document(resume_file)
                for paragraph in doc.paragraphs:
                    if paragraph.text:
                        resume_text += paragraph.text + "\n"
            else:
                return Response(
                    {"error": "Unsupported file format. Please upload a valid .pdf or .docx file."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Validation guard check to see if text extraction succeeded
            if not resume_text.strip():
                return Response(
                    {"error": "Could not extract readable text from the uploaded document template."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        except Exception as e:
            return Response(
                {"error": f"Failed parsing document structural layouts: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        

        # 2. Fetch the Groq API Key
        groq_key = os.environ.get("GROQ_API_KEY")
        if not groq_key:
            return Response(
                {"error": "Groq API key missing in environment configuration (.env)"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # 3. Query the Groq inference engine
        try:
            client = Groq(api_key=groq_key)
            
            prompt = f"""
            You are an expert ATS (Applicant Tracking System) optimizer. Analyze the provided resume text against the target job description text.
            
            Resume Text:
            {resume_text}
            
            Job Description Text:
            {job_description}
            
            Provide a detailed comparison analysis. You must return your entire output as a single, perfectly structured JSON object.
            The JSON object structure must exactly match these keys (all keys are lowercase strings):
            {{
                "match_score": <integer between 0 and 100>,
                "skills": [<list of strings representing top 5 relevant technical skills identified>],
                "feedback": {{
                    "strengths": [<list of strings detailing core strengths matching the job requirements>],
                    "gaps": [<list of strings detailing critical requirements or keywords absent from the resume>]
                }}
            }}
            """

            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a precise data analysis engine that outputs strictly structured validation schemas in clean JSON formatting."
                    },
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.3
            )

            ai_response_string = completion.choices[0].message.content
            parsed_json_payload = json.loads(ai_response_string)
            
            original_filename = resume_file.name if hasattr(resume_file, 'name') else 'Resume.pdf'
            current_time = timezone.now()
            formatted_timestamp = current_time.strftime("%Y-%m-%d %H:%M:%S")

            
            raw_score = parsed_json_payload.get("match_score") or parsed_json_payload.get("matchScore") or 0
            try:
                extracted_score = int(raw_score)
            except (ValueError, TypeError):
                extracted_score = 0
            
            
            extracted_skills = parsed_json_payload.get("skills") or parsed_json_payload.get("extracted_skills") or []
            if not isinstance(extracted_skills, list):
                extracted_skills = []

           
            extracted_feedback = parsed_json_payload.get("feedback")
            if not isinstance(extracted_feedback, dict):
                extracted_feedback = {
                    "strengths": parsed_json_payload.get("strengths") if isinstance(parsed_json_payload.get("strengths"), list) else [],
                    "gaps": parsed_json_payload.get("gaps") if isinstance(parsed_json_payload.get("gaps"), list) else []
                }
            else:
                if "strengths" not in extracted_feedback or not isinstance(extracted_feedback["strengths"], list):
                    extracted_feedback["strengths"] = []
                if "gaps" not in extracted_feedback or not isinstance(extracted_feedback["gaps"], list):
                    extracted_feedback["gaps"] = []

           
            with transaction.atomic():
                resume_instance = Resume.objects.create(
                    user=request.user,
                    file=resume_file,
                    extracted_text=resume_text
                )
                
                JobAnalysis.objects.create(
                    user=request.user,
                    resume=resume_instance,
                    job_description=job_description,
                    match_score=extracted_score,
                    feedback=extracted_feedback,  
                    analyzed_at=current_time
                )

            
            secured_response = {
                "match_score": extracted_score,
                "skills": extracted_skills,
                "feedback": extracted_feedback,
                "filename": original_filename,
                "analyzed_at": formatted_timestamp
            }

            return Response(secured_response, status=status.HTTP_200_OK)

        except json.JSONDecodeError:
            return Response(
                {"error": "AI returned an invalid data structure layout. Please retry."}, 
                status=status.HTTP_502_BAD_GATEWAY
            )
        except Exception as e:
            logger.error(f"Groq Core Analysis Exception: {str(e)}", exc_info=True)
            return Response(
                {"error": f"Groq Processing Failure occurred: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        

class DashboardHistoryView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            scans = JobAnalysis.objects.filter(user=request.user).order_by('-analyzed_at')
            history_records = []
            
            # Explicitly target Indian Standard Time zone natively
            indian_tz = ZoneInfo('Asia/Kolkata')
            
            for scan in scans:
                filename = "Unknown_Resume.pdf"
                if scan.resume and scan.resume.file:
                    filename = os.path.basename(scan.resume.file.name)
                
                if scan.analyzed_at:
                    # Natively convert the database time to absolute IST
                    local_timestamp = scan.analyzed_at.astimezone(indian_tz)
                    timestamp_string = local_timestamp.strftime("%Y-%m-%d %H:%M:%S")
                else:
                    timestamp_string = timezone.now().astimezone(indian_tz).strftime("%Y-%m-%d %H:%M:%S")

                history_records.append({
                    "filename": filename,
                    "analyzed_at": timestamp_string, 
                    "match_score": getattr(scan, 'match_score', 0)
                })
            
            return Response(history_records, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({"error": "Failed to load history Ledger"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

       