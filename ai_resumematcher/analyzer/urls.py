from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterView, ResumeAnalyzeView, DashboardHistoryView

urlpatterns = [
    path('api/register/', RegisterView.as_view(), name='auth_register'),
    path('api/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/analyze/', ResumeAnalyzeView.as_view(), name='resume_analyze'),
    path('api/history/', DashboardHistoryView.as_view(), name='dashboard_history'),
]