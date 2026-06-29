from django.urls import path
from .views import AuditCreateView, AuditHistoryView, AuditDetailView

urlpatterns = [
    path('audit/', AuditCreateView.as_view(), name='audit-create'),
    path('audits/', AuditHistoryView.as_view(), name='audit-history'),
    path('audits/<int:pk>/', AuditDetailView.as_view(), name='audit-detail'),
]