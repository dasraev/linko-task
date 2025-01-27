from django.urls import path
from .views import ReportListApiView
urlpatterns = [
    path('report',ReportListApiView.as_view()),
]