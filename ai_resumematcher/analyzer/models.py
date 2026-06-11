
from django.db import models
from django.contrib.auth.models import User

class Resume(models.Model):
    """
    Stores raw file data buffers and extracted metadata parameters inside PostgreSQL
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resumes')
    file = models.FileField(upload_to='resumes/')
    extracted_text = models.TextField(blank=True, null=True)
    extracted_skills = models.JSONField(default=list, blank=True) # Binary JSON fields natively inside Postgres
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.file.name}"


class JobAnalysis(models.Model):
    """
    Tracks structured relational performance records mapping candidate resumes to criteria
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='analyses')
    job_description = models.TextField()
    match_score = models.IntegerField() # Numeric Integer field scores 0 - 100
    feedback = models.JSONField(default=dict) # High-speed unstructured text structures dictionary data array blocks
    analyzed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Analysis Match ID: {self.id} for {self.user.username} ({self.match_score}%)"
    
